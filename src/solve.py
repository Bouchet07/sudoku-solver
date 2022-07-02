import numpy as np


valid_numbers = np.arange(10)
list_numbers = valid_numbers[1:]
set_numbers = set(list_numbers)

def load_sudoku(file_path: str, delimiter: str=',') -> np.ndarray:
    """
    Reads a file conta ining a sudoku and returns (if it's valid) the sudoku

    (by default reads csv files)

    Parameters
    ----------
    file_path : str
        The file path
    delimiter : str, optional
        The delimiter separating the values of the file, by default ','

    Returns
    -------
    Sudoku
        The sudoku
    """
    sudoku = np.genfromtxt(file_path, delimiter=delimiter, dtype=np.uint8)
    if valid_sudoku(sudoku): return sudoku
    raise ValueError(f'sudoku not valid')

def valid_sudoku(sudoku: np.ndarray) -> bool:
    """Checks if a sudoku is valid to solve

    Parameters
    ----------
    sudoku : np.ndarray
        The sudoku

    Returns
    -------
    bool
        True if valid
    """
    shape = [value for value in sudoku.shape if value != 1]

    dim = len(shape) == 2 and \
          shape[0] == shape[1] == 9

    num = np.all(np.isin(sudoku, valid_numbers))

    return dim and num

def check_sudoku(sudoku: np.ndarray) -> bool:
    """Checks if a sudoku is solved

    Parameters
    ----------
    sudoku : np.ndarray
        The sudoku

    Returns
    -------
    bool
        True if solved
    """
    rows = all([set(r)==set_numbers for r in sudoku])
    cols = all([set(r)==set_numbers for r in np.transpose(sudoku)])

    q1 = set(sudoku[:3, :3].flatten())==set_numbers
    q2 = set(sudoku[:3, 3:6].flatten())==set_numbers
    q3 = set(sudoku[:3, 6:].flatten())==set_numbers

    q4 = set(sudoku[3:6, :3].flatten())==set_numbers
    q5 = set(sudoku[3:6, 3:6].flatten())==set_numbers
    q6 = set(sudoku[3:6, 6:].flatten())==set_numbers

    q7 = set(sudoku[6:, :3].flatten())==set_numbers
    q8 = set(sudoku[6:, 3:6].flatten())==set_numbers
    q9 = set(sudoku[6:, 6:].flatten())==set_numbers

    return all([rows, cols, q1, q2, q3, q4, q5, q6, q7, q8, q9])

def generate_sudoku(file_path=None, difficulty='hard'):
    if difficulty == 'easy': numbersin = 30
    elif difficulty == 'medium': numbersin = 24
    elif difficulty == 'hard': numbersin = 17
    else: raise ValueError(f'{difficulty = } is invalid try easy, medium or hard)')

    diag = np.array(list_numbers, dtype=np.uint8)
    np.random.shuffle(diag)
    sudoku = solve(np.diag(diag))[0]
    idx = np.random.choice(np.arange(9*9), size = 9*9-numbersin, replace=False)
    sudoku.ravel()[idx] = 0
    if file_path:
        np.savetxt(file_path, sudoku, delimiter=',', fmt='%i')
    return sudoku


def pretty_print(sudoku):
    base = 3
    side  = base*base

    def expandLine(line):
        return line[0]+line[5:9].join([line[1:5]*(base-1)]*base)+line[9:13]
    line0  = expandLine("╔═══╤═══╦═══╗")
    line1  = expandLine("║ . │ . ║ . ║")
    line2  = expandLine("╟───┼───╫───╢")
    line3  = expandLine("╠═══╪═══╬═══╣")
    line4  = expandLine("╚═══╧═══╩═══╝")

    symbol = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nums   = [ [""]+[symbol[n] for n in row] for row in sudoku ]

    print(line0)
    for r in range(1,side+1):
        print( "".join(n+s for n,s in zip(nums[r-1],line1.split("."))) )
        print([line2,line3,line4][(r%side==0)+(r%base==0)])


def solve(sudoku, max_solutions=1, interactive=False, _sudoku_solutions=None):
    if _sudoku_solutions is None: _sudoku_solutions = []
    if max_solutions == 'max': max_solutions = np.inf
    for y0, x0 in zip(*np.where(sudoku==0)):
        for n in range(1,10):
            if possible(sudoku, y0,x0,n):
                sudoku[y0,x0] = n
                solve(sudoku, max_solutions, interactive, _sudoku_solutions)
                if len(_sudoku_solutions) < max_solutions:
                    sudoku[y0,x0] = 0

        return _sudoku_solutions
    if interactive:
        pretty_print(sudoku)
        input('otra solución?')
    _sudoku_solutions.append(sudoku.copy())
    return _sudoku_solutions

# def solve_interactive(sudoku: np.ndarray):
#     for y0, x0 in zip(*np.where(sudoku==0)):
#         for n in range(1,10):
#             if possible(sudoku, y0,x0,n):
#                 sudoku[y0,x0] = n
#                 solve_interactive(sudoku)
#                 sudoku[y0,x0] = 0
#         return
    
#     pretty_print(sudoku)
#     input('otra solución?')
    

def possible(sudoku: np.ndarray, y: int, x: int, n: int) -> bool:
    """Checks if it's possible to place n in (y,x) position in the sudoku

    Parameters
    ----------
    sudoku : np.ndarray
        _description_
    y : int
        y position
    x : int
        x position
    n : int
        number to check

    Returns
    -------
    bool
        True if possible
    """
    if np.any(sudoku[y] == n): return False
    if np.any(sudoku[:,x] == n): return False

    x0 = x//3 * 3
    y0 = y//3 * 3
    
    if np.any(sudoku[y0:y0+3, x0:x0+3] == n): return False
    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Sudoku Solver')

    parser.add_argument('file_path',
                        nargs='+',
                        metavar='file path',
                        help='file path to unsolved sudoku')

    parser.add_argument('-n','--number',
                        default=1,
                        metavar='val',
                        help='max number of sudokus (default: 1, no limit: \'max\')')

    parser.add_argument('-g','--generate',
                        action='store_true',
                        help='generates unsolved sudokus')

    parser.add_argument('-d','--difficulty',
                        default='hard',
                        metavar='val',
                        nargs='+',
                        help='difficulty of generated sudoku (default: \'hard\', \'medium\', \'easy\')')    

    args = parser.parse_args()
    file_path = args.file_path[0]
    generate = args.generate
    difficulty = args.difficulty[0]

    try:
        max_solutions = int(args.number)
    except:
        max_solutions = 'max'

    if generate:
        generated = generate_sudoku(file_path, difficulty=difficulty)
        pretty_print(generated)
        print(f'succesfully saved to {file_path}')
    else:
        sudoku = load_sudoku(file_path)
        solve(sudoku, max_solutions=max_solutions, interactive=True)
    # file_path = args[0]

    # if len(sys.argv) > 3: raise ValueError(f'only supports 2 arguments, file_path, max=1')
    # elif len(sys.argv) == 3: FILE_PATH, max_iter = str(sys.argv[1]), int(sys.argv[2])
    # elif len(sys.argv) == 2: FILE_PATH, max_iter = str(sys.argv[1]), 1
    # else: raise ValueError(f'needs the file path')

    # sudoku = load_sudoku(FILE_PATH)
    # solve(sudoku, max_iter, interactive=True)

if __name__ == '__main__':
    main()



