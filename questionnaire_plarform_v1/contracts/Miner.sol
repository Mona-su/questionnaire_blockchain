pragma solidity >=0.4.22 <0.6.0;
import "./Questionnaire.sol";

contract Miner {
    // address of Questionnaire contract
    address public questionnaireAddress;
    Questionnaire theQuestionnaire;

    modifier waitMiningNotEmpty (){
        require (theQuestionnaire.waitMiningCount() > 0, "No questionnaire wait mining. ");
        _;
    }

    constructor (
        address _questionnaireAddress
    )
        public
    {
        questionnaireAddress = _questionnaireAddress;
        theQuestionnaire = Questionnaire(address(_questionnaireAddress));
    }

    function mineQuestionnaire ()
        public
        waitMiningNotEmpty
    {
        uint256 _questionnaireId = theQuestionnaire.questionnaireMined();

    }

}
