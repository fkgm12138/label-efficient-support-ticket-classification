"""Check saved evidence via its real verification entry point."""
from pathlib import Path
import subprocess,sys,unittest
R=Path(__file__).resolve().parents[1]
class EvidenceTests(unittest.TestCase):
 def test_reference_evidence(self):
  proc=subprocess.run([sys.executable,str(R/'verify_results.py')],cwd=R,capture_output=True,text=True,encoding='utf-8')
  self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
if __name__=='__main__':unittest.main()
