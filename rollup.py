from typing import Dict, List, Optional, Set
from urllib import request
import sys
import json
from dataclasses import dataclass
import xlsxwriter


@dataclass
class Part:
    id: int
    parent_part_id: Optional[int]
    part_id: int
    quantity: int
    total_quantity: Optional[int] = None


class BillOfMaterial:
    def __init__(self) -> None:
        self.bom_tree: Dict[int, List[Part]] = {}
        self.bom_tree_parent: Dict[int, Set[int]] = {}

    def load_data(self) -> None:
        """Load data from the BOM end point and create a tree of materials."""

        with request.urlopen('https://interviewbom.herokuapp.com/bom/') as req:
            bom = json.load(req)

        for record in bom['data']:
            part = Part(**record)
            if part.part_id not in self.bom_tree:
                self.bom_tree[part.part_id] = [part]
            else:
                self.bom_tree[part.part_id].append(part)

    def get_part_no(self, part_id: int) -> str:
        """Get part number from Part end point."""

        with request.urlopen(f"https://interviewbom.herokuapp.com/part/{part_id}/") as req:
            part = json.load(req)
        return part['part_number']

    def parent_exclude_set(self, part_id: int) -> Set[int]:
        """Return parents of a Part which has been used before and should be excluded."""

        if part_id not in self.bom_tree_parent:
            self.bom_tree_parent[part_id] = set()
        return self.bom_tree_parent[part_id]

    def calc_total_quantity(self, part_id: int, exclude_set: Set[int] = set()) -> Optional[Part]:
        """Calculate total quantities of a Part by multiplying its parent total quantity to its quantity."""

        result: Optional[Part] = None

        for part in self.bom_tree[part_id]:
            if result is None and part.id not in exclude_set:
                result = part

            if part.total_quantity is None:

                if part.parent_part_id is None:
                    part.total_quantity = part.quantity
                else:
                    parent_exclude_set = self.parent_exclude_set(part.part_id)
                    parent_part = self.calc_total_quantity(
                        part.parent_part_id, parent_exclude_set)
                    part.total_quantity = parent_part.total_quantity * part.quantity
                    parent_exclude_set.add(parent_part.id)

        return result

    def get_bom_list(self) -> List:
        """Get bill of materials."""

        result = []

        for part_id in self.bom_tree.keys():
            self.calc_total_quantity(part_id)

            total = sum(
                map(lambda part: part.total_quantity, self.bom_tree[part_id]))
            part_number = self.get_part_no(part_id)

            result.append([part_number, total])

        return result

    def rollup(self, output_file: str):
        """Rollup BoM and store in an excel sheet."""
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet()

        bom_list = self.get_bom_list()

        for item, idx in enumerate(bom_list):
            worksheet.write(f"A{idx+1}", item[0])
            worksheet.write(f"B{idx+1}", item[1])

        workbook.close()


if __name__ == '__main__':
    try:
        if len(sys.argv) < 2:
            print('Error: you should specify output file in the arguments.')
            exit(1)
        bof = BillOfMaterial()
        bof.load_data()
        bof.rollup(sys.argv[1])
        print(f"BOM has been created and saved in '{sys.argv[1]}'")

    except:
        print("Rollup process has been failed!")
