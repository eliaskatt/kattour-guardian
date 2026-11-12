import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import visual_compare

try:
    from PIL import Image
except ImportError:
    Image = None


@unittest.skipIf(Image is None, 'Pillow is optional')
class VisualCompareTests(unittest.TestCase):
    def test_identical_and_one_pixel(self):
        with TemporaryDirectory() as root:
            a = Path(root) / 'a.png'
            b = Path(root) / 'b.png'
            Image.new('RGB', (10, 10), 'white').save(a)
            Image.new('RGB', (10, 10), 'white').save(b)
            self.assertEqual(visual_compare.compare_pair(a, b)['status'], 'identical')
            image = Image.open(b).copy()
            image.putpixel((3, 4), (0, 0, 0))
            image.save(b)
            report = visual_compare.compare_pair(a, b)
            self.assertEqual(report['changed_pixels'], 1)
            self.assertEqual(report['changed_percent'], 1.0)
            self.assertEqual(report['bounding_box'], [3, 4, 4, 5])

    def test_dimensions_and_threshold(self):
        with TemporaryDirectory() as root:
            a, b = Path(root)/'a.png', Path(root)/'b.png'
            Image.new('RGB', (10, 10), 'white').save(a)
            Image.new('RGB', (15, 10), 'white').save(b)
            self.assertEqual(visual_compare.compare_pair(a, b)['status'], 'dimension_mismatch')
            Image.new('RGB', (10, 10), (250, 250, 250)).save(b)
            self.assertEqual(visual_compare.compare_pair(a, b, threshold=15)['status'], 'identical')
            self.assertEqual(visual_compare.compare_pair(a, b, threshold=1)['changed_pixels'], 100)

    def test_directories_and_no_pixels_in_report(self):
        with TemporaryDirectory() as root:
            a, b = Path(root)/'a', Path(root)/'b'
            a.mkdir(); b.mkdir()
            for name in visual_compare.VIEWPORTS:
                Image.new('RGB', (20, 20), 'white').save(a / f'guardian-{name}.png')
                Image.new('RGB', (20, 20), 'black').save(b / f'guardian-{name}.png')
            report = visual_compare.compare_directories(a, b)
            self.assertEqual(report['status'], 'review_required')
            self.assertNotIn(str(a), str(report))
            self.assertNotIn('data:', str(report))

    def test_reject_symlink(self):
        with TemporaryDirectory() as root:
            file, link = Path(root)/'a.png', Path(root)/'link.png'
            Image.new('RGB', (2,2), 'black').save(file)
            link.symlink_to(file)
            with self.assertRaises(ValueError):
                visual_compare.open_image(link)


if __name__ == '__main__':
    unittest.main()
