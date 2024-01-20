from neo4j import GraphDatabase
import json

class Connection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get(self, message):
        with self.driver.session() as session:
            response = session.execute_write(self.send_message, message)
            return response

    @staticmethod
    def send_message(tx, query):
        result = tx.run(query)
        result_json = json.dumps([r.data() for r in result])
        return result_json



def query_neo4j(query):
    neo4j_database = Connection("bolt://localhost:7687", "neo4j", "password")
    response = neo4j_database.get(query)
    neo4j_database.close()
    return response