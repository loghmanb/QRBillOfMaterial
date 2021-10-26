import json
import unittest
from unittest.mock import patch, MagicMock

from rollup import BillOfMaterial


class RollupTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.bom = BillOfMaterial()

    def test_rollup(self):
        url_return = {'data': [
            {
                'id': 0,
                'parent_part_id': None,
                'part_id': 1,
                'quantity': 1
            },
            {
                'id': 1,
                'parent_part_id': 1,
                'part_id': 2,
                'quantity': 2
            },
            {
                'id': 2,
                'parent_part_id': 2,
                'part_id': 3,
                'quantity': 4
            },
            {
                'id': 3,
                'parent_part_id': 3,
                'part_id': 4,
                'quantity': 3
            },
            {
                'id': 4,
                'parent_part_id': 3,
                'part_id': 4,
                'quantity': 3
            },
            {
                'id': 5,
                'parent_part_id': 1,
                'part_id': 5,
                'quantity': 5
            },
            {
                'id': 6,
                'parent_part_id': 1,
                'part_id': 3,
                'quantity': 2
            },
        ]}

        with patch('rollup.request.urlopen') as mock_urlopen:
            cm = MagicMock()
            cm.getcode.return_value = 200
            cm.read.return_value = json.dumps(url_return)
            cm.__enter__.return_value = cm
            mock_urlopen.return_value = cm

            self.bom.load_data()

        part_numbers = {
            1: "24-81240-Q",
            2: "24-97828-T",
            3: "24-54669-G",
            4: "24-60136-L",
            5: "24-53167-W",
        }

        with patch('rollup.BillOfMaterial.get_part_no',
                   side_effect=lambda x: part_numbers[x]) as mock_part_no:
            result = self.bom.get_bom_list()
            assert result == [
                ['24-81240-Q', 1],
                ['24-97828-T', 2],
                ['24-54669-G', 10],
                ['24-60136-L', 30],
                ['24-53167-W', 5],
            ]


if __name__ == '__main__':
    unittest.main()
