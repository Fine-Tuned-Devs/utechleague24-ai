import os

import pinecone


def get_user_index_name(username: str) -> str:
    """
    Generates a unique index name for each user.

    Args:
        username (str): The username for which to create the index name.

    Returns:
        str: The generated index name.
    """
    return f"user-{username}-index"


class PineconeHelper:
    def __init__(self):
        """
        Initializes the Pinecone client using the provided API key.
        """
        self.pc = pinecone.Pinecone(api_key=os.getenv("CONNECTION_STRINGS_PINECONE"))

    def create_user_index(self, username: str, dimension: int):
        """
        Creates a Pinecone index for a specific user if it does not already exist.

        Args:
            username (str): The username for which to create the index.
            dimension (int): The dimension of the vectors to be stored in the index.

        Returns:
            Index: The created or existing Pinecone index.
        """
        index_name = get_user_index_name(username)
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine',
                spec=pinecone.ServerlessSpec(cloud='aws', region='us-east-1')
            )
        return self.pc.Index(index_name)

    def insert_vector(self, username: str, id: str, vector: list, dimension: int):
        """
        Inserts or updates a vector in the user's Pinecone index.

        Args:
            username (str): The username whose index is being updated.
            id (str): The unique identifier for the vector.
            vector (list): The vector data.
            dimension (int): The dimension of the vector.

        Raises:
            ValueError: If the dimension of the vector does not match the specified dimension.
        """
        if len(vector) != dimension:
            raise ValueError(f"Vector dimension should be {dimension}")
        index = self.create_user_index(username, dimension)
        upsert_data = [{"id": id, "values": vector}]
        index.upsert(vectors=upsert_data)

    def query_vector(self, username: str, vector: list, top_k: int, dimension: int):
        """
        Queries the user's Pinecone index for the most similar vectors.

        Args:
            username (str): The username whose index is being queried.
            vector (list): The query vector.
            top_k (int): The number of top similar vectors to return.
            dimension (int): The dimension of the query vector.

        Returns:
            dict: The query results.

        Raises:
            ValueError: If the dimension of the vector does not match the specified dimension.
        """
        if len(vector) != dimension:
            raise ValueError(f"Vector dimension should be {dimension}")
        index = self.pc.Index(get_user_index_name(username))
        return index.query(vector=vector, top_k=top_k, include_values=True)

    def delete_vector(self, username: str, id: str, dimension: int):
        """
        Deletes a vector from the user's Pinecone index.

        Args:
            username (str): The username whose index is being updated.
            id (str): The unique identifier of the vector to delete.
            dimension (int): The dimension of the vectors in the index.
        """
        index = self.create_user_index(username, dimension)
        index.delete(ids=[id])

    def fetch_vector(self, username: str, id: str, dimension: int):
        """
        Fetches a vector from the user's Pinecone index by its ID.

        Args:
            username (str): The username whose index is being queried.
            id (str): The unique identifier of the vector to fetch.
            dimension (int): The dimension of the vectors in the index.

        Returns:
            dict: The fetched vector.
        """
        index = self.create_user_index(username, dimension)
        return index.fetch(ids=[id])

    def describe_user_index(self, username: str, dimension: int):
        """
        Describes the statistics of the user's Pinecone index.

        Args:
            username (str): The username whose index is being described.
            dimension (int): The dimension of the vectors in the index.

        Returns:
            dict: The index statistics.
        """
        index = self.create_user_index(username, dimension)
        return index.describe_index_stats()

    def update_index_data(self, username: str, id: str, new_namespace: str, vector: list):
        """
        Inserts a new namespace into the user's index.

        Args:
            username (str): The username whose index is being updated.
            id (str): The unique identifier for the vector.
            new_namespace (str): The new namespace to add the vector to.
            vector (list): The vector data.

        Raises:
            ValueError: If the dimension of the vector does not match the specified dimension.
        """
        index_name = get_user_index_name(username)
        index = self.pc.Index(index_name)
        index.upsert(vectors=[{"id": id, "values": vector}], namespace=new_namespace)

    def get_message_by_id(self, username: str, id: str, dimension: int):
        """
        Retrieves the message stored in the metadata of a vector by its ID.

        Args:
            username (str): The username whose index is being queried.
            id (str): The unique identifier of the vector to fetch.
            dimension (int): The dimension of the vectors in the index.

        Returns:
            str: The message stored in the metadata, or None if not found.
        """
        index = self.create_user_index(username, dimension)
        response = index.fetch(ids=[id])
        if id in response['vectors']:
            return response['vectors'][id].get('metadata', {}).get('original_data', None)
        return None
