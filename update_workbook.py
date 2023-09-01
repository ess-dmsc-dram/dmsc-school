import json
from enum import auto, Enum
from pathlib import Path
from types import MappingProxyType
from typing import Optional


# Configuration Variables
SYNC_FILE_SUFFIXES = ('.py', '.ipynb', '.png', '.jpg', '.svg')
EXCLUDE_DIRS = ('__pycache__', '.ipynb_checkpoints')
WORKBOOK_ROOT_DIR = Path('workbooks')
SOURCE_REPLACEMENT_MESSAGE = '# Insert your solution:\n'
CELL_PROTECTING_TAG = 'dmsc-school-keep'


class GitStatus(Enum):
    DELETED = auto()
    MODIFIED = auto()
    ADDED = auto()
    UNTRACKED = auto()
    TOUCHED = auto()


git_prefix_to_status = MappingProxyType({
    'D  ': GitStatus.DELETED,
    ' M ': GitStatus.MODIFIED,
    'A  ': GitStatus.ADDED,
    '?? ': GitStatus.UNTRACKED
})


class Lecture(Enum):
    PYTHONBASICS = auto()
    PROPOSALS = auto()
    MCSTAS = auto()
    SCIPP = auto()
    MODEL = auto()
    SCICAT = auto()


lecture_to_directories = MappingProxyType({
    Lecture.PYTHONBASICS: Path('1-python'),
    Lecture.PROPOSALS: Path('2-proposals'),
    Lecture.MCSTAS: Path('3-mcstas'),
    Lecture.SCIPP: Path('4-reduction'),
    Lecture.MODEL: Path('5-analysis'),
    Lecture.SCICAT: Path('6-scicat'),
})


# Helper Utilities
# Helper - Git
def run_git_command(*args: str) -> str:
    import subprocess
    if 'rm' in args and '--cached' not in args:
        raise RuntimeError("Using `git rm` without --cached option is not allowed.")

    return subprocess.run(['git', *args], stdout=subprocess.PIPE, text=True).stdout


def git_changed_files(git_base: str = './') -> dict[Path, GitStatus]:
    git_status = run_git_command('-C', git_base, 'status', '-s')
    return {
        Path(file_status[3:]): git_prefix_to_status[status]
        for file_status in git_status.split('\n')
        if (status:=file_status[:3]) in git_prefix_to_status
    }


def git_root() -> Path:
    git_root = run_git_command('rev-parse', '--show-toplevel')
    return Path(git_root.rstrip())


def report_updates() -> None:
    changed_list = git_changed_files(git_base=str(WORKBOOK_ROOT_DIR))

    if changed_list:
        print("Updates done.")
        print("There are updates in the workbooks to be committed.")
        
        print("\nHint:\n",
            "cd workbooks\n",
            *(f"git add {str(filepath)}\n" for filepath in changed_list),
            "git commit -m '{COMMITMESSAGE}'\n",
            "git push origin {BRANCHNAME}")
    else:
        print("Nothing to update.")


# Helper - System Commands
def check_current_dir():
    import os
    if (cur_file_dir:=Path(__file__).parent) != git_root() \
        or cur_file_dir != Path(os.getcwd()):
        raise RuntimeError("`update_workbook` should be run in "
                           "the `dmsc-school` root directory, where this script is."
                           f"hint: cd {cur_file_dir.resolve()}")


def flat_dir(dirs: list[Path], files: Optional[list[Path]] = None) -> list:
    if files is None:
        files = []

    if not dirs:
        return files    

    if (dir:=dirs.pop()).is_file() and dir.suffix in SYNC_FILE_SUFFIXES:
        files.append(dir)
    elif dir.is_dir() and dir.name not in EXCLUDE_DIRS:
        import os
        dirs.extend([dir/Path(file) for file in os.listdir(dir)])
    
    return flat_dir(dirs, files)


def listmaterials(root_dir: Path) -> list:
    from itertools import chain
    return list(chain(
        *(flat_dir(dirs=[root_dir/lecture_dir])
        for lecture_dir
        in lecture_to_directories.values()
        if lecture_dir.exists())
    ))


def get_all_materials() -> dict:
    textbook_list = listmaterials(root_dir=Path('./'))
    workbook_list = listmaterials(root_dir=WORKBOOK_ROOT_DIR)

    materials = dict()
    for workbook in workbook_list:
        if workbook not in textbook_list:
            materials[workbook] = GitStatus.DELETED

    for textbook in textbook_list:
        materials[textbook] = GitStatus.TOUCHED

    return materials


def export_raw_material(textbook_path: Path) -> None:
    """Copy python materials to the workbook directory."""
    
    import shutil, os
    if not (workbook_dir:=WORKBOOK_ROOT_DIR/textbook_path.parent).exists():
        os.makedirs(workbook_dir)

    shutil.copy(textbook_path, workbook_dir)


# Helper - Jupyter Contents
def retrieve_tags(cell: dict[str, dict]) -> list:
    return meta.get('tags', []) if (meta:=cell.get('metadata')) else []


def check_tags(cell: dict[str, dict], tag_flags: dict[str, bool]) -> bool:
    return (cell_tags:=retrieve_tags(cell)) is not None and \
            all([tag in cell_tags if flag else tag not in cell_tags 
                 for tag, flag in tag_flags.items()])


def is_hidden_solution_cell(cell: dict[str, dict]) -> bool:
    return check_tags(cell, {'solution': True, CELL_PROTECTING_TAG: False})


def is_workbook_cell(cell: dict[str, dict]) -> bool:
    return not check_tags(cell, {'remove-cell': True, CELL_PROTECTING_TAG: False})


class Textbook:
    """Jpyter notebook for lectures."""
    def __init__(self, rel_path: Path) -> None:
        self.rel_path = rel_path
        self.contents = self._load_contents()
        self.workbook_path = WORKBOOK_ROOT_DIR/self.rel_path
        self.workbook = self._create_workbook_contents()

    def _create_workbook_contents(self) -> dict:
        """
        Update workbook(ipynb) from the textbook contents.

        How to create a workbook from a textbook
        ----------------------------------------
        For all cells without ``dmsc-school-keep`` tag (``CELL_PROTECTING_TAG``).
        1. Remove all cells containing ``remove-cell``.
        2. Replace source code with ``SOURCE_REPLACEMENTM_MESSAE``
           of all cells containing ``solution`` tags,
           and replace ``hide-cell``, ``solution`` tags with ``workbook`` tag.
        
        """
        from copy import deepcopy
        workbook = deepcopy(self.contents)
        workbook['cells'] = list(filter(is_workbook_cell, workbook.get('cells', [])))
        solution_cells = filter(is_hidden_solution_cell, workbook.get('cells', []))
        
        for solution in solution_cells:
            solution['source'] = [SOURCE_REPLACEMENT_MESSAGE]
            tags = retrieve_tags(solution)
            for tag in ('hide-cell', 'solution'):
                if tag in tags:
                    tags.remove(tag)
            if 'workbook' not in tags:
                tags.append('workbook')

        return workbook

    def _load_contents(self) -> dict:
        with open(self.rel_path) as file:
            return json.load(file)
    
    def export_workbook(self) -> None:
        if not self.workbook_path.parent.exists():
            self.workbook_path.parent.mkdir(parents=True)

        with open(self.workbook_path, 'w') as file:
            json.dump(self.workbook, file, indent=1)
            file.write('/n')


def is_in_lecture_dirs(file_path: Path, lecture_dirs: Optional[list[Path]] = None) -> bool:
    if lecture_dirs is None:
        lecture_dirs = list(lecture_to_directories.values())

    if (dir:=file_path.parent).parent == Path('.'):
        return dir in lecture_dirs

    return is_in_lecture_dirs(dir, lecture_dirs=lecture_dirs)


def filter_textbooks(changed_files: dict) -> dict[Path, GitStatus]:
    changed_materials = {
        filepath: status
        for filepath, status in changed_files.items()
        if filepath.suffix in SYNC_FILE_SUFFIXES
    }
    return {
        file_path: status
        for file_path, status in changed_materials.items()
        if is_in_lecture_dirs(file_path)
    }


def delete_workbook(workbook_path: Path):
    if workbook_path.exists():
        run_git_command('-C', str(WORKBOOK_ROOT_DIR), 'rm', '--cached', str(workbook_path))


def update_workbooks(textbooks: dict):
    
    for textbook_path, status in textbooks.items():
        if status == GitStatus.DELETED:
            delete_workbook(textbook_path)
        elif textbook_path.suffix == '.ipynb':
            textbook = Textbook(textbook_path)
            textbook.export_workbook()
        else:
            export_raw_material(textbook_path)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-a', '--all', dest="scope_all", help="Update all workbooks.", action="store_true")
    args = parser.parse_args()
    
    check_current_dir()

    if args.scope_all:
        candidates = get_all_materials()
    else:
        candidates = git_changed_files()
    
    textbooks = filter_textbooks(candidates)
    update_workbooks(textbooks)
    report_updates()

