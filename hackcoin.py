import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []      # Must be declared before create_block
        self.create_block(proof=1, previous_hash='0')   # Create the Genesis block
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain),
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []      # After block creation, the transactions need to be cleared so that they are not reused
        self.chain.append(block)
        
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def add_transaction(self, sender, recipient, amount):
        self.transactions.append({'sender': sender,
                                  'recipient': recipient,
                                  'amount': amount})
        # Return the index of the new block in which these transactions will be included
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    # Consensus
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length:
                    max_length = length
                    longest_chain = chain
                    
        if longest_chain:
            self.chain = longest_chain
            return True
        
        return False
    
    def proof_of_work(self, previous_proof):
        # This will be the calculation the miners will have to complete in order to mine the block
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    def hash(self, block):
        # This will hash the entire block
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        # Go through the entire blockchain and make sure each block is valid
        while block_index < len(chain):
            block = chain[block_index]
            
            # Check to see if the current block's "previous block" hash and the previous block's actual hash are =
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            # Check if the current block's proof of work is correct
            previous_proof = previous_block['proof']
            proof = block['proof']
            
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True
    