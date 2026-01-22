from flask import Blueprint, request, jsonify

local_api = Blueprint("local_api", __name__)

# Fake memory blockchain
local_votes = {1: 0, 2: 0, 3: 0}
local_voters = set()


@local_api.route("/results", methods=["GET"])
def local_results():
    return jsonify({
        "1": local_votes[1],
        "2": local_votes[2],
        "3": local_votes[3]
    })


@local_api.route("/vote", methods=["POST"])
def local_vote():
    data = request.json
    wallet = data.get("wallet")
    cid = int(data.get("candidateId"))

    if wallet in local_voters:
        return jsonify({"error": "Already voted"}), 400

    local_voters.add(wallet)
    local_votes[cid] += 1

    return jsonify({"success": True})


@local_api.route("/hasVoted", methods=["GET"])
def local_has_voted():
    wallet = request.args.get("wallet")
    return jsonify({"hasVoted": wallet in local_voters})


