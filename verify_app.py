import requests
import unittest

BASE_URL = "http://127.0.0.1:5000"

class TestVotingApp(unittest.TestCase):
    def test_voting_flow(self):
        # 1. Get index to get a cookie
        s = requests.Session()
        r = s.get(BASE_URL)
        print(f"Index status: {r.status_code}")
        self.assertEqual(r.status_code, 200)
        
        cookies = s.cookies.get_dict()
        print(f"Cookies: {cookies}")
        self.assertTrue('user_hash' in cookies or len(cookies) > 0) # Flask might set it on response

        # 2. Vote for Candidate 1
        vote_data = {'candidate_id': 1, 'score': 5}
        r = s.post(f"{BASE_URL}/vote", json=vote_data)
        print(f"Vote response: {r.text}")
        self.assertEqual(r.status_code, 200)

        # 3. Try to vote again for Candidate 1 (should fail)
        r = s.post(f"{BASE_URL}/vote", json=vote_data)
        print(f"Duplicate vote response: {r.text}")
        self.assertNotEqual(r.status_code, 200)

        # 4. Check results
        r = s.get(f"{BASE_URL}/results")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Alice Johnson", r.text)

if __name__ == '__main__':
    unittest.main()
