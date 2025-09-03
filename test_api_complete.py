import requests
import json
from datetime import datetime

class BugTrackerAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.project_id = None
        self.bug_id = None
        self.comment_id = None

    def authenticate(self, username, password):
        print(" Step 1: Authentication")
        
        response = requests.post(f"{self.base_url}/auth/login/", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access']
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"✅ Login successful")
            print(f"   Access Token: {self.token[:50]}...")
            return True
        else:
            print(f"Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    def test_projects(self):
        print("\n Step 2: Testing Project Endpoints")
        
        # Create project
        project_data = {
            "name": f"Python Test Project {datetime.now().strftime('%H:%M:%S')}",
            "description": "Testing project endpoints with Python"
        }
        
        response = requests.post(f"{self.base_url}/projects/", 
                               headers=self.headers, 
                               json=project_data)
        
        if response.status_code == 201:
            self.project_id = response.json()['id']
            print(f"Project created successfully (ID: {self.project_id})")
        else:
            print(f"Project creation failed: {response.status_code}")
            return False
        
        # List projects
        response = requests.get(f"{self.base_url}/projects/", headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                projects = data['results']
            else:
                projects = data
            # projects = response.json()['results']
            print(f"Projects listed: {len(projects)} projects found")
        
        # Get specific project
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/", 
                              headers=self.headers)
        if response.status_code == 200:
            print(f"Project details retrieved")
        
        # Update project
        response = requests.patch(f"{self.base_url}/projects/{self.project_id}/", 
                                headers=self.headers, 
                                json={"description": "Updated description"})
        if response.status_code == 200:
            print(f"Project updated successfully")
        
        return True

    def test_bugs(self):
        print("\n Step 3: Testing Bug Endpoints")
        
        # Create bug
        bug_data = {
            "title": "Python API Test Bug",
            "description": "This bug was created automatic via API test",
            "priority": "high",
            "project": self.project_id
        }
        
        response = requests.post(f"{self.base_url}/bugs/", headers=self.headers, json=bug_data)
        
        if response.status_code == 201:
            self.bug_id = response.json()['id']
            print(f" Bug created successfully (ID: {self.bug_id})")
        else:
            print(f" Bug creation failed: {response.status_code}")
            return False
        
        # List bugs
        response = requests.get(f"{self.base_url}/bugs/", headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                bugs = data['results']
            else:
                bugs = data  
            print(f"Bugs listed: {len(bugs)} bugs found")
        
        # Test filtering
        filters = [
            ("status", "open"),
            ("priority", "high"),
            ("project", str(self.project_id))
        ]
        
        for filter_name, filter_value in filters:
            response = requests.get(f"{self.base_url}/bugs/?{filter_name}={filter_value}", headers=self.headers)
            if response.status_code == 200:
                count = len(response.json()['results'])
                print(f" Filter by {filter_name}={filter_value}: {count} bugs")
        
        # Update bug status
        response = requests.patch(f"{self.base_url}/bugs/{self.bug_id}/", headers=self.headers, json={"status": "in_progress"})
        if response.status_code == 200:
            print(f"Bug status updated to 'in_progress'")
        
        # Test search
        response = requests.get(f"{self.base_url}/bugs/?search=Python", headers=self.headers)
        if response.status_code == 200:
            count = len(response.json()['results'])
            print(f"Search functionality: {count} bugs found")
        
        # Get assigned bugs
        response = requests.get(f"{self.base_url}/bugs/assigned_to_me/", headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                count = data['results']
            else:
                count = len(data)
            print(f"Assigned bugs: {count} bugs assigned to user")
        
        return True

    def test_comments(self):
        print("\n Step 4: Testing Comment Endpoints")
        
        # Create comment
        comment_data = {
            "bug": self.bug_id,
            "message": "This is another test comment"
        }
        
        response = requests.post(f"{self.base_url}/comments/", headers=self.headers, json=comment_data)
        
        if response.status_code == 201:
            self.comment_id = response.json()['id']
            print(f" Comment created successfully (ID: {self.comment_id})")
        else:
            print(f" Comment creation failed: {response.status_code}")
            return False
        
        # List comments
        response = requests.get(f"{self.base_url}/comments/", headers=self.headers)
        if response.status_code == 200:
            comments = response.json()['results']
            print(f" Comments listed: {len(comments)} comments found")
        
        # Filter comments by bug
        response = requests.get(f"{self.base_url}/comments/?bug={self.bug_id}", headers=self.headers)
        if response.status_code == 200:
            count = len(response.json()['results'])
            print(f" Comments for bug {self.bug_id}: {count} comments")
        
        # Update comment
        response = requests.patch(f"{self.base_url}/comments/{self.comment_id}/", headers=self.headers, 
                                json={"message": "Updated comment message"})
        if response.status_code == 200:
            print(f" Comment updated successfully")
        
        return True

    def test_error_cases(self):
        print("\n  Step 5: Testing Error Cases")
        
        # Test without authentication
        response = requests.get(f"{self.base_url}/projects/")
        if response.status_code == 401:
            print(" Unauthenticated request properly rejected (401)")
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{self.base_url}/projects/", headers=invalid_headers)
        if response.status_code == 401:
            print(" Invalid token properly rejected (401)")
        # Test non-existent resource
        response = requests.get(f"{self.base_url}/bugs/99999/", headers=self.headers)
        if response.status_code == 404:
            print(" Non-existent resource returns 404")
        
        # Test invalid data
        response = requests.post(f"{self.base_url}/bugs/", headers=self.headers, json={"title": ""}) 
        if response.status_code == 400:
            print("Invalid data properly rejected (400)")
        
        return True

    def run_complete_test(self, username="admin", password="admin123"):
        print(" Starting Complete API Testing")
        print("=" * 60)
        
        success = True
        
        # Step 1: Authentication
        success &= self.authenticate(username, password)
        
        if not success:
            print(" Authentication failed. Cannot continue.")
            return False
        
        # Step 2: Projects
        success &= self.test_projects()
        
        # Step 3: Bugs
        success &= self.test_bugs()
        
        # Step 4: Comments
        success &= self.test_comments()
        
        # Step 5: Error cases
        success &= self.test_error_cases()
        
        print("\n" + "=" * 60)
        if success:
            print(" ALL TESTS PASSED SUCCESSFULLY!")
            print(f"   Created Project ID: {self.project_id}")
            print(f"   Created Bug ID: {self.bug_id}")
            print(f"   Created Comment ID: {self.comment_id}")
        else:
            print(" Some tests failed.")
        
        return success

if __name__ == "__main__":
    tester = BugTrackerAPITester()
    tester.run_complete_test()