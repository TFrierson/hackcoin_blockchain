from hackcoin import Blockchain
from flask import Flask, jsonify, request
from uuid import uuid4


# Mining

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create an address for this node
node_address = str(uuid4()).replace('-', '')

# Create a blockchain
blockchain = Blockchain()       # This will also create our Genesis block

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    
    # Coinbase
    blockchain.add_transaction(node_address, 'Tiffany', 100)
    
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    
    return jsonify(response), 200


# Adding a new transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    # The transactions will be included in a file hosted on Postman
    json = request.get_json(cache=False)
    
    # Check that there are no missing keys in the JSON file
    transaction_keys = ['sender', 'recipient', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    
    index = blockchain.add_transaction(json['sender'], json['recipient'], json['amount'])
    response = {'message': f'This transaction was added to Block: {index}'}
    return jsonify(response), 201

# Decentralizing the Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    # The nodes addresses will be in a file hosted on Postman
    json = request.get_json(cache=False)
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes found', 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message': 'All the nodes are now connected. The Hackcoin Blockchain now contains the following nodes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain with the longest chain if necessary
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    chain_replaced = blockchain.replace_chain()
    if chain_replaced:
        response = {'message': 'The blockchain had to be replaced', 'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain did not need to be replaced', 'actual_chain': blockchain.chain}
    
    return jsonify(response), 200


# Get the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    chain_valid = blockchain.is_chain_valid(blockchain.chain)
    response = {'blockchain_valid': chain_valid}
    
    return jsonify(response), 200


# Running the app
app.run(host= '0.0.0.0', port=3001)