var Questionnaire = artifacts.require("./Questionnaire.sol");

module.exports = function(deployer) {
  deployer.deploy(Questionnaire);
};
