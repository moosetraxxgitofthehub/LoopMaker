import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from processing import make_loop, LoopError, tool

def ff(*args):
    return subprocess.check_output([tool('ffmpeg'), '-v', 'error', '-nostdin', *map(str, args)], stderr=subprocess.STDOUT)
def metadata(path):
    return json.loads(subprocess.check_output([tool('ffprobe'), '-v','error','-show_streams','-show_format','-of','json',str(path)]))

class ProcessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='LoopMaker test spaces ')
        cls.folder = Path(cls.temp.name)
        cls.source = cls.folder / 'video with spaces.mp4'
        ff('-f','lavfi','-i','testsrc2=size=160x120:rate=12:duration=2','-f','lavfi','-i','sine=duration=2','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',cls.source)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def test_speeds_and_frame_order(self):
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        for speed in (0.5,1.0,1.5):
            with self.subTest(speed=speed):
                output = make_loop(self.source, speed)
                self.assertTrue(output.name.startswith(f'video with spaces_LOOP_{speed:.1f}x'))
                data = metadata(output)
                self.assertEqual(len(data['streams']),1)
                stream = data['streams'][0]
                self.assertEqual(stream['codec_name'],'h264')
                self.assertEqual((stream['width'],stream['height']),(160,120))
                self.assertEqual(stream['pix_fmt'],'yuv420p')
                self.assertAlmostEqual(float(data['format']['duration']),4/speed,delta=0.18)
                raw = ff('-i',output,'-f','rawvideo','-pix_fmt','gray','-')
                size = 160*120
                frames = [raw[i:i+size] for i in range(0,len(raw),size)]
                self.assertEqual(len(frames)%2,0)
                # Reencoded forward/reverse images should match despite inter-frame codec noise.
                diffs = [sum(abs(a-b) for a,b in zip(x,y))/size for x,y in zip(frames, reversed(frames))]
                self.assertLess(max(diffs),3)
                # Confirm forward half matches speed-normalized original, not merely a palindrome.
                expected = ff('-i',self.source,'-vf',f'setpts=PTS-STARTPTS,setpts=PTS/{speed},fps=12','-an','-f','rawvideo','-pix_fmt','gray','-')
                self.assertEqual(len(expected),len(raw)//2)
                self.assertLess(sum(abs(a-b) for a,b in zip(expected,raw[:len(expected)]))/len(expected),3)
        self.assertEqual(before,hashlib.sha256(self.source.read_bytes()).hexdigest())
    def test_formats(self):
        for ext,codec in [('mov','libx264'),('webm','libvpx-vp9'),('mkv','libx264'),('avi','mpeg4')]:
            with self.subTest(format=ext):
                source = self.folder / f'common format.{ext}'
                ff('-i',self.source,'-an','-c:v',codec,source)
                self.assertTrue(make_loop(source,1.0).is_file())
    def test_duration_boundary(self):
        for duration in (10,10.1):
            source = self.folder / f'length {duration}.mp4'
            ff('-f','lavfi','-i',f'testsrc2=size=32x32:rate=10:duration={duration}','-c:v','libx264',source)
            if duration == 10:
                result = make_loop(source,0.5)
                self.assertAlmostEqual(float(metadata(result)['format']['duration']),40,delta=0.2)
            else:
                with self.assertRaisesRegex(LoopError,'10 seconds'): make_loop(source,1.0)
    def test_duplicate_preservation(self):
        first = make_loop(self.source,0.8)
        digest = hashlib.sha256(first.read_bytes()).hexdigest()
        second = make_loop(self.source,0.8)
        self.assertNotEqual(first,second)
        self.assertEqual(digest,hashlib.sha256(first.read_bytes()).hexdigest())
    def test_errors(self):
        bad = self.folder/'corrupt.mp4'
        bad.write_text('not a video')
        with self.assertRaises(LoopError): make_loop(bad,1.0)
        with self.assertRaises(LoopError): make_loop(self.folder/'missing.mp4',1.0)
        with self.assertRaises(LoopError): make_loop(self.source,2.0)

if __name__ == '__main__': unittest.main()
