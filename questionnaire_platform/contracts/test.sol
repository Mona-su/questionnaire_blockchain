pragma solidity >=0.4.22 <0.6.0;

contract Test{
    bytes public a_val = hex"00000000000000000000000000000000000000000000bccc69e47d98498430b725f7ff5af5be936fb1ccde3fdcda3b0882a9082eab761e75b34da18d8923d70b481d89e2e936eecec248b3d456b580900a18bcd39b3948bc956139367b89dde7";
    uint256[8][] public b_val;
    uint256[2][2][2] public c_val;
    function getLength() public view returns(uint256) {
        return a_val.length;
    }

    function passBytes(uint256[8][] memory _input) public {
        // b_val.push("0x123");
        // b_val.push("apple");
        b_val = _input;
    }

    function test3dArray() public returns (uint256[2][2][2] memory) {
        for (uint256 i = 0; i < 2; i++) {
            for (uint256 j = 0; j < 2; j++) {
                for(uint256 k = 0; k < 2; k++) {
                    c_val[i][j][k] = (i+1)*100 + (j+1)*10 + (k+1);
                }
            }
        }
        return c_val;
    }
}
