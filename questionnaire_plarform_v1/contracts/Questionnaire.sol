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

     uint256[16] public N; // N = pq
     uint256[16] public g; // g = -u^(2N) mod N^2, u in Z*(N^2)
     uint256[16] public h2; // h2 from SQS

     /* uint256[] public waitMining;
     uint256 public waitMiningCount; */

     address public SQS;

     // struct Question {
     //     uint256 id;
     //     string content;
     //     // 1: rating scale questions
     //     // 2: multiple choice questions
     //     // 3: rank order questions
     //     // 4: dichotomous questions (yes or no)
     //     uint questionType;
     //     uint256 multiplicationResult;
     // }

     struct Participant {
         uint256 questionnaireId;
         uint256 participantId;
         uint256[16][] m1;
         uint256[16][] m2;
     }

     struct OneQeustionnaire {
         uint256 id;
         address QP; // address of question provider
         uint256 publicKey; // h1 = g^a mod N^2
         // uint256 secretKey; // a in [1, N^2/4], kept by QP self
         uint256 questionCount;
         string questionTitle;
         string questionContents;
         uint256[] questionTypes;
         uint256 participantCount;
         uint256[16][] cm1;
         uint256[16][] cm2;
         uint256[16][] cm1_prime;
         uint256[16][] cm2_prime;
         uint256[16][100][100] matrix;
         bool closed;
         bool computed;
     }

     event questionnaireAdded (
         uint256 id
     );

     event participantAdded (
         uint256 questionnaireId,
         uint256 participantId
     );

     event requiredMining (
         uint256 questionnaireId
     );

     event questionnaireMined (
         uint256 questionnaireId
     );

     event questionnairePartialDecrypted(uint256 questionnaireId);

     modifier questionnaireExist(uint256 _questionnaireId) {
         require(questionnaireCount > 0 && _questionnaireId <= questionnaireCount, "Questionnaire not existing. ");
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
         uint256 _primeP,
         uint256 _primeQ
     )
         public
     {
         // require (_primeP > 10 && _primeQ > 10, "prime numbers too small"); // might be unnecessary
         SQS = msg.sender;
         questionnaireCount = 0;
         currentQnId = 0;
         N = _primeP.mul(_primeQ);
         // todo: compute g; how to?
         uint256 u = 3;
         g = (-(u ** (2*N))).mod(N*N);
         // random number generating
         b = (uint256(keccak256(abi.encodePacked(block.timestamp)))).mod((N**2).div(4));
         h2 = (g**b).mod(N**2);
         waitMiningCount = 0;
     }

     // all the questions will be sent as a json from the front-end app
     function addQuestionnaire (
         string memory _questionContents,
         string memory _title,
         uint[] memory _questionTypes,
         uint _questionCount,
         uint256 _publicKey
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
         // for (uint i = 0; i < _questionCount; i++) {
         //     questionnaires[currentQnId].questions.push(Question(i, _questionContents, _questionTypes[i], 0));
         // }
         emit questionnaireAdded (currentQnId);
     }


     // the front-end will pass the encrypted answers to blockchain
     // as questionnaires is public, participants could get all info (including public key for encrypting)
     function addParticipant (
         uint256 _questionnaireId,
         uint256[8][] memory _cm1,
         uint256[8][] memory _cm2
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


    function requireMining (
        uint256 _questionnaireId
    )
        public
        questionnaireExist(_questionnaireId)
        onlyQP(_questionnaireId)
    {
        /* waitMining.push(_questionnaireId);
        waitMiningCount++; */
        emit requiredMining(_questionnaireId);
    }

    function questionnaireMining (
        uint256 _questionnaireId,
        uint256[16][] _cm1,
        uint256[16][] _cm2
    )
        public
        questionnaireExist(_questionnaireId)
    {
        /* uint256 _id = waitMining[0];
        delete waitMining[0]; */
        questionnaires[_questionnaireId].cm1 = _cm1;
        questionnaires[_questionnaireId].cm2 = _cm2;
        emit questionnaireMined(_questionnaireId);
        /* return _id; */
    }

    function questionnairePartialDecrypting (
        uint256 _questionnaireId,
        uint256[16][] _cm1prime,
        uint256[16][] _cm2prime
    )
        public
        questionnaireExist(_questionnaireId)
        onlySQS
    {
        questionnaires[_questionnaireId].cm1prime = _cm1prime;
        questionnaires[_questionnaireId].cm2prime = _cm2prime;
        emit questionnairePartialDecrypted(_questionnaireId);
    }

    /* function getAverage (
        uint256 _questionnaireId,
        uint256 _questionNo,
        uint256 _privateKey,
        uint _questionType
    )
        public
        onlyQP
        view
        returns (uint)
    {
        require (_questionType == 1 || _questionType == 3);
        require (questionnaires[questionnaireId].computed, "Wait for miner computing the answers.");
        uint256 c1, c2, c1prime, c2prime;
        // call miner to compute and pass E(m1 + m2 + ...), how to?
        // call SQS to partial decrypt using b
        var(c1prime, c2prime) = _getAverageSQSDecrypt (c1, c2);
        // call QP to again decrypt using a
        uint256 sum = _getAverageQPDecrypt (c1prime, c2prime, _privateKey);
        uint256 avg = sum.div(questionnaires[_questionnaireId].questionCount);
        emit averageGenerated ();
        return avg;
    }

    function getAverageSQSDecrypt (
        uint256 _c1,
        uint256 _c2
    )
        public
        view
        onlySQS
        returns (uint256, uint256)
    {
        uint256 temp = _c2**b;
        uint256 _c2prime =
    } */

}
