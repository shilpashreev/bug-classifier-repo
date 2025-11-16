# test_classifier.py
import unittest
import os
import json
from classifier import classify_bug_report, BugClassification

# Define paths relative to the test_classifier.py file
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
JSON_BUG_PATH = os.path.join(TEST_DATA_DIR, "bug_report.json")
XML_FEATURE_PATH = os.path.join(TEST_DATA_DIR, "feature_request.xml")

class TestBugClassifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Setup test data files once for all tests."""
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        
        # JSON Bug Report (Expected to be classified as a valid bug)
        json_data = {
            "bug_id": "B-405",
            "title": "Button click sometimes does nothing on checkout page",
            "description": "After adding items to cart, navigating to the checkout page and clicking the 'Place Order' button sometimes fails to proceed, and there is no error message. Happens about 1 in 5 tries.",
            "reporter": "Jane Doe",
            "severity": "Major",
        }
        with open(JSON_BUG_PATH, "w") as f:
            json.dump(json_data, f, indent=4)
            
        # XML Feature Request (Expected to be classified as NOT a valid bug)
        xml_data = """
        <issue_report>
            <id>I-201</id>
            <type>Request</type>
            <summary>Improve documentation for the new API endpoint</summary>
            <detail>The documentation for the /api/v2/users endpoint is missing examples for authentication.</detail>
            <submitter>John Smith</submitter>
        </issue_report>
        """
        with open(XML_FEATURE_PATH, "w") as f:
            f.write(xml_data)

    def test_01_classify_json_bug(self):
        """Test classification of a valid JSON-formatted bug report."""
        print("\n--- Running Test 1: JSON Bug Classification ---")
        result = classify_bug_report(JSON_BUG_PATH, BugClassification)
        
        # 1. Assert Structure and Validity
        self.assertIsInstance(result, dict, "Result should be a dictionary.")
        self.assertTrue("priority" in result, "Result is missing the 'priority' field.")
        self.assertTrue(result.get("is_valid_bug"), "Bug report should be classified as a valid bug.")
        
        # 2. Assert Classification Values (using expected classifications for this type of issue)
        self.assertIn(result.get("priority"), ["High", "Medium"], "Priority should be High or Medium.")
        self.assertIn(result.get("component"), ["UI", "Backend"], "Component should be UI or Backend.")
        
        print(f"Classification: {result}")

    def test_02_classify_xml_feature_request(self):
        """Test classification of an XML-formatted feature request (should be invalid bug)."""
        print("\n--- Running Test 2: XML Feature Request Classification ---")
        result = classify_bug_report(XML_FEATURE_PATH, BugClassification)
        
        # 1. Assert Structure and Validity
        self.assertIsInstance(result, dict, "Result should be a dictionary.")
        self.assertFalse(result.get("is_valid_bug"), "Feature request should be classified as NOT a valid bug.")
        
        # 2. Assert Classification Values (should default to Low/Testing/etc. if invalid)
        self.assertIn(result.get("priority"), ["Low", "Medium"], "Feature request priority should typically be Low.")
        
        print(f"Classification: {result}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test data files after all tests are done."""
        os.remove(JSON_BUG_PATH)
        os.remove(XML_FEATURE_PATH)
        os.rmdir(TEST_DATA_DIR)


if __name__ == '__main__':
    # Add a safety check for the API key before running tests
    if not os.getenv("GOOGLE_API_KEY"):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! WARNING: GOOGLE_API_KEY environment variable is NOT set.      !!!")
        print("!!! The tests that rely on the Gemini API will likely fail.       !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    unittest.main()
