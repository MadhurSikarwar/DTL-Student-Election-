// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Election {
    // Store vote counts for ANY candidate ID
    mapping(uint256 => uint256) public votes;
    
    // Total votes cast
    uint256 public totalVotes;
    
    // Event to log votes for the frontend/backend listener
    event Voted(uint256 indexed candidateId);

    // Dynamic Vote Function
    // Accepts ANY positive integer as candidateId
    function vote(uint256 candidateId) public {
        require(candidateId > 0, "Invalid Candidate ID");
        
        votes[candidateId] += 1;
        totalVotes += 1;
        
        emit Voted(candidateId);
    }

    // Helper to get votes for a specific candidate
    function getVotes(uint256 candidateId) public view returns (uint256) {
        return votes[candidateId];
    }
}
