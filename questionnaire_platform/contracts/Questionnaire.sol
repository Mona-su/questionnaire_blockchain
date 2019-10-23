pragma solidity >=0.4.22 <0.6.0;
/* pragma experimental ABIEncoderV2; */
import "./SafeMath.sol";

contract Questionnaire {
    using SafeMath for uint256;

     // delete a mapping: delete questionnaires[id]
     mapping(uint256 => OneQeustionnaire) public questionnaires;
     uint256 public questionnaireCount;
     uint256 public currentQnId; // currentQnId of questionnaire, counting from 1

     mapping(uint256 => Participant) public participants; // map participantId to Participant

     mapping(address => uint256) public balances;

     uint256[16] public N; // N = pq
     uint256[16] public g; // g = -u^(2N) mod N^2, u in Z*(N^2)
     uint256[16] public h2; // h2 from SQS

     address public SQS;


     struct Participant {
         uint256 questionnaireId;
         uint256 participantId;
         uint256[16][] m1;
         uint256[16][] m2;
     }

     struct OneQeustionnaire {
         uint256 id;
         address QP; // address of question provider
         uint256[16] publicKey; // h = h1*h2%(N^2)
         uint256 questionCount;
         bytes questionTitle;
         bytes questionContents;
         /*
            1. rating scale question
            2. multiple choice question
            3. rank order question
            4. dichotomous question
          */
         uint256[] questionTypes;
         uint256 participantCount;
         uint256[16][] cm1;
         uint256[16][] cm2;
         uint256[16][] cm1prime;
         uint256[16][] cm2prime;
         uint256[16][100][100] matrix1;
         uint256[16][100][100] matrix2;
         bool closed;
         bool computed;
     }

     /* participant listens to it */
     event questionnaireAdded (
         uint256 _id
     );

     event participantAdded (
         uint256 _questionnaireId,
         uint256 _participantId
     );

     /* miner listens to it */
     event requiredMining (
         uint256 _questionnaireId
     );

     /* miner listens to it */
     event requiredMatrix(
         uint256 _questionnaireId,
         uint256 _problemId
     );

     /* SQS listens to it */
     event requiredMiningWithId(
         uint256 _questionnaireId,
         uint256 _problemId,
         uint256 _participantId
     );

     /* SQS listens to it */
     event questionnaireMined (
         uint256 _questionnaireId
     );

     /* SQS listens to it */
     event matrixMined(
         uint256 _questionnaireId,
         uint256 _problemId
     );

     /* QP listens to it */
     event questionnairePartialDecrypted(
         uint256 _questionnaireId
     );

     /* QP listens to it */
     event matrixPartialDecrypted(
         uint256 _questionnaireId,
         uint256 _problemId
     );

     /* QP listens to it */
     event questionPartialDecryptedWithId (
         uint256 _questionnaireId,
         uint256 _problemId,
         uint256 _participantId,
         uint256[16] _cm1prime,
         uint256[16] _cm2prime
     );

     /* SQS listens to it */
     event requiredWithdrawToken (
         address _to,
         uint256 _amount
     );

     /* miner listens to it */
     event withdrawCompleted (
         address _from,
         address _to,
         uint256 _amount
     );


     modifier questionnaireExist(uint256 _questionnaireId) {
         require(questionnaireCount > 0 && _questionnaireId <= questionnaireCount, "Questionnaire not existing. ");
         _;
     }

     modifier questionTypeForMatrix(uint256 _questionnaireId, uint256 _problemId) {
         require(questionnaires[_questionnaireId].questionTypes[_problemId] == 1, "Not able to build matrix with this question type.");
         _;
     }

     modifier onlyQP (uint256 _questionnaireId) {
         require (questionnaires[_questionnaireId].QP == msg.sender, "You are not the owner of the questionnaire.");
         _;
     }

     modifier onlySQS() {
         require(msg.sender == SQS, "You are not SQS. ");
         _;
     }


     constructor
     (
         uint256[16] memory _N ,
         uint256[16] memory _g,
         uint256[16] memory _h2
     )
         public
     {
         SQS = msg.sender;
         questionnaireCount = 0;
         currentQnId = 0;
         N = _N;
         g = _g;
         h2 = _h2;
     }


     // all the questions will be sent as a json from the front-end app
     function addQuestionnaire (
         bytes memory _questionContents,
         bytes memory _title,
         uint[] memory _questionTypes,
         uint _questionCount,
         uint256[16] memory _publicKey
     )
         public
     {
         questionnaireCount ++;
         currentQnId++;
         questionnaires[currentQnId].id = currentQnId;
         questionnaires[currentQnId].QP = msg.sender;
         questionnaires[currentQnId].publicKey = _publicKey;
         questionnaires[currentQnId].questionCount = _questionCount;
         questionnaires[currentQnId].participantCount = 0;
         questionnaires[currentQnId].closed = false;
         questionnaires[currentQnId].computed = false;
         questionnaires[currentQnId].questionContents = _questionContents;
         questionnaires[currentQnId].questionTitle = _title;
         questionnaires[currentQnId].questionTypes = _questionTypes;
         emit questionnaireAdded (currentQnId);
     }


     // the front-end will pass the encrypted answers to blockchain
     function addParticipant (
         uint256 _questionnaireId,
         uint256[16][] memory _cm1,
         uint256[16][] memory _cm2
     )
         public
         questionnaireExist(_questionnaireId)
     {
         uint256 _index = questionnaires[_questionnaireId].participantCount++;
         _index += (_questionnaireId - 1).mul(100);
         participants[_index].questionnaireId = _questionnaireId;
         participants[_index].participantId = questionnaires[_questionnaireId].participantCount;
         participants[_index].m1 = _cm1;
         participants[_index].m2 = _cm2;
         emit participantAdded (_questionnaireId, questionnaires[_questionnaireId].participantCount);
     }


     function getQuestionnaireTitle(
         uint256 _questionnaireId
     )
        public
        view
        returns(bytes memory)
    {
        return questionnaires[_questionnaireId].questionContents;
    }


    function getQuestionnaireContent(
        uint256 _questionnaireId
    )
       public
       view
       returns(bytes memory)
   {
       return questionnaires[_questionnaireId].questionTitle;
   }


   function getQuestionnaireKey(
       uint256 _questionnaireId
   )
       public
       view
       returns(
           uint256[16] memory
       )
   {
       return questionnaires[_questionnaireId].publicKey;
   }


   function getQuestionnaireQCount(
       uint256 _questionnaireId
   )
       public
       view
       returns(
           uint256
       )
   {
       return questionnaires[_questionnaireId].questionCount;
   }


   function getQuestionnaireQTypes(
       uint256 _questionnaireId
   )
       public
       view
       returns(
           uint256[] memory
       )
   {
       return questionnaires[_questionnaireId].questionTypes;
   }


   function getQuestionnaireParCount(
       uint256 _questionnaireId
   )
       public
       view
       returns(
           uint256
       )
   {
       return questionnaires[_questionnaireId].participantCount;
   }


   function getParticipantAnswer(
       uint256 _participantId,
       uint256 _questionnaireId
   )
        public
        view
        returns(uint256[16][] memory, uint256[16][] memory)
    {
        uint256 _index = (_questionnaireId.sub(1)).mul(100) + _participantId;
        return (participants[_index].m1, participants[_index].m2);
    }


    function getQuestionnaireResult(
        uint256 _questionnaireId,
        uint256 _step
    )
        public
        view
        returns(uint256[16][] memory, uint256[16][] memory)
    {
        if (_step == 1){
            return (questionnaires[_questionnaireId].cm1, questionnaires[_questionnaireId].cm2);
        }
        else {
            return (questionnaires[_questionnaireId].cm1prime, questionnaires[_questionnaireId].cm2prime);
        }
    }


    function getQuestionnaireMatrix(
        uint256 _questionnaireId
    )
        public
        view
        returns(uint256[16][100][100] memory, uint256[16][100][100] memory)
    {
        return (questionnaires[_questionnaireId].matrix1, questionnaires[_questionnaireId].matrix2);
    }


    function requireMining (
        uint256 _questionnaireId
    )
        public
        questionnaireExist(_questionnaireId)
        onlyQP(_questionnaireId)
    {
        emit requiredMining(_questionnaireId);
    }


    function requireMatrix (
        uint256 _questionnaireId,
        uint256 _problemId // counting from 0
    )
        public
        questionnaireExist(_questionnaireId)
        onlyQP(_questionnaireId)
        questionTypeForMatrix(_questionnaireId, _problemId)
    {
        emit requiredMatrix(_questionnaireId, _problemId);
    }


    function requireMiningWithId (
        uint256 _questionnaireId,
        uint256 _problemId,
        uint256 _participantId
    )
        public
        questionnaireExist(_questionnaireId)
        onlyQP(_questionnaireId)
        questionTypeForMatrix(_questionnaireId, _problemId)
    {
        require(_participantId > 0 && _participantId <= questionnaires[_questionnaireId].participantCount, "Invalid participant id.");
        emit requiredMiningWithId(_questionnaireId, _problemId, _participantId);
    }


    function questionnaireMining (
        uint256 _questionnaireId,
        uint256[16][] memory _cm1,
        uint256[16][] memory _cm2
    )
        public
        questionnaireExist(_questionnaireId)
    {
        questionnaires[_questionnaireId].cm1 = _cm1;
        questionnaires[_questionnaireId].cm2 = _cm2;
        balances[msg.sender]++;
        emit questionnaireMined(_questionnaireId);
    }


    function matrixMining (
        uint256 _questionnaireId,
        uint256 _problemId, // counting from 0
        uint256[16][100][100] memory _matrix1,
        uint256[16][100][100] memory _matrix2
    )
        public
        questionnaireExist(_questionnaireId)
        questionTypeForMatrix(_questionnaireId, _problemId)
    {
        questionnaires[_questionnaireId].matrix1 = _matrix1;
        questionnaires[_questionnaireId].matrix2 = _matrix2;
        balances[msg.sender]++;
        emit matrixMined(_questionnaireId, _problemId);
    }


    function questionnairePartialDecrypting (
        uint256 _questionnaireId,
        uint256[16][] memory _cm1prime,
        uint256[16][] memory _cm2prime
    )
        public
        questionnaireExist(_questionnaireId)
        onlySQS
    {
        questionnaires[_questionnaireId].cm1prime = _cm1prime;
        questionnaires[_questionnaireId].cm2prime = _cm2prime;
        emit questionnairePartialDecrypted(_questionnaireId);
    }


    function matrixPartialDecrypting (
        uint256 _questionnaireId,
        uint256 _problemId, // counting from 0
        uint256[16][100][100] memory _matrix1,
        uint256[16][100][100] memory _matrix2
    )
        public
        onlySQS
        questionnaireExist(_questionnaireId)
        questionTypeForMatrix(_questionnaireId, _problemId)
    {
        questionnaires[_questionnaireId].matrix1 = _matrix1;
        questionnaires[_questionnaireId].matrix2 = _matrix2;
        emit matrixPartialDecrypted(_questionnaireId, _problemId);
    }


    function questionPartialDecryptingWithId (
        uint256 _questionnaireId,
        uint256 _problemId,
        uint256 _participantId,
        uint256[16] memory _cm1prime,
        uint256[16] memory _cm2prime
    )
        public
        questionnaireExist(_questionnaireId)
        onlySQS
        questionTypeForMatrix(_questionnaireId, _problemId)
    {
        emit questionPartialDecryptedWithId (_questionnaireId, _problemId, _participantId, _cm1prime, _cm2prime);
    }

    function requireWithdrawToken(
        uint256 _amount
    )
        public
    {
        require(balances[msg.sender] >= _amount, "Required amount exceeds account balance. ");
        balances[msg.sender] -= _amount;
        emit requiredWithdrawToken(msg.sender, _amount);
    }

    function helpWithdraw (
        address payable _to,
        uint256 _amount
    )
        public
        payable
        onlySQS
    {
        _to.transfer(msg.value*_amount);
        emit withdrawCompleted(msg.sender, _to, _amount);
    }

}
