using System.Security.Cryptography;
using System.Drawing;
using System.Numerics;

namespace game_of_life;

class Board
{
    public Vector2 _tileSize;
    public Vector2 _currDims;
    public Vector2 _newDims;
    public List<List<Tile>> _tiles = new List<List<Tile>>();
    public int _livingCells;
    public int _generation;
    public List<int>[] _mode = new List<int>[2] { new List<int>{ 3 }, new List<int>{ 3, 2 } };

    public Board(Vector2 tileSize, Vector2 boardSize)
    {
        _tileSize = tileSize;
        UpdateDimensions(boardSize);
    }

    public void UpdateDimensions(Vector2 boardSize)
    {
        // new dimensions saved ready for next population
        _newDims = boardSize / _tileSize;
    }

    public Vector2 GetSize(bool old=false)
    {
        // whether to pass the current set of dimensions or the new set (screen rect)
        if (old) return _currDims * _tileSize;

        else return _newDims * _tileSize;
    }
    
    public void FlipTile(Vector2 pos)
    {
        // for when tile is clicked
        Vector2 boardSize = GetSize(old: true);
        if (pos.X < boardSize.X && pos.Y < boardSize.Y)
        {
            Vector2 coords = pos / _tileSize;
            _tiles[(int)coords.Y][(int)coords.X].ChangeType(flip: true);
        }
    }

    public void Populate(PopType popType, float? percentage=null)
    {
        // update values
        _tiles = new List<List<Tile>>();
        _livingCells = 0;
        _generation = 0;
        _currDims = _newDims;

        int[] colorCombo = new int[] {1, 2, 3, 4};
        Random rng = new Random();
        rng.Shuffle(colorCombo);

        for (int x = 0; x < _currDims.X; x++)
        {
            List<Tile> row = new List<Tile>();
            for (int y = 0; y < _currDims.Y; y++)
            {
                // possible colour segments dependant on position
                int[] colors = new int[] { (int)Math.Round(x * 255 / _currDims.X),
                                           (int)Math.Round(y * 255 / _currDims.Y),
                                           255 - (int)Math.Round(x * 255 / _currDims.X),
                                           255 - (int)Math.Round(y * 255 / _currDims.Y),
                                           255 };
                // random 3 of the 5 possibilities
                Color color = Color.FromArgb(colors[colorCombo[0]], colors[colorCombo[1]], colors[colorCombo[2]]);

                // determine whether tile is living or dead
                bool tileState = popType switch 
                {
                    PopType.Percentage => rng.NextSingle() < percentage,
                    PopType.Checkerboard => (x + y) % 2 == 1,
                    PopType.Lines => x % 2 == 1,
                    PopType.Edges => x == 0 || x == _currDims.X - 1 || y == 0 || y == _currDims.Y - 1,
                    _ => false
                };

                _livingCells += tileState ? 1 : 0;
                row.Add(new Tile(this, tileState, new Vector2(x, y), color));
            }
            _tiles.Add(row);
        }

        foreach (List<Tile> row in _tiles)
        {
            foreach (Tile tile in row) tile.UpdateNeighbors();
        }
    }

    public void neighborCheck()
    {
        foreach (List<Tile> row in _tiles)
        {
            foreach (Tile tile in row) tile.CheckNeighbors();
        }
    }

    public void Update_tiles()
    {
        // tiles switched to their new state
        foreach (List<Tile> row in _tiles)
        {
            foreach (Tile tile in row) tile.ChangeType();
        }
        _generation += 1;
    }
}

class Tile
{
    public Board _board;
    public bool _state;
    public bool _newState;
    public Vector2 _coord;
    public Color _color;
    public List<Tile> _neighbors = new List<Tile>();

    public Tile(Board board, bool state, Vector2 coord, Color color)
    {
        _board = board;
        _state = state;
        _coord = coord;
        _color = color;
    }

    public void UpdateNeighbors()
    {
        int x = (int)_coord.X;
        int y = (int)_coord.Y;
        int bX = (int)_board._currDims.X;
        int bY = (int)_board._currDims.Y;

        // creates neighbors based on position of tile
        int bottom_x = (x != 0 ? x - 1 : bX - 1);
        int top_x    = (x != bX - 1 ? x + 1 : 0);
        int bottom_y = (y != 0 ? y - 1 : bY - 1);
        int top_y    = (y != bY - 1 ? y + 1 : 0);

        _neighbors = new List<Tile>{ _board._tiles[y][bottom_x],
                                     _board._tiles[y][top_x],
                                     _board._tiles[bottom_y][x],
                                     _board._tiles[top_y][x],
                                     _board._tiles[bottom_y][bottom_x],
                                     _board._tiles[top_y][top_x],
                                     _board._tiles[top_y][bottom_x],
                                     _board._tiles[bottom_y][top_x] };
    }

    public void ChangeType(bool flip=false)
    {
        if (flip)  // for clicking on individual cells
        {
            _state = !_state;
            _board._livingCells += (_state) ? 1 : -1;
        }
        else  // for editing all cells at once
        {
            _state = _newState;
        }
    }

    public void CheckNeighbors()
    {
        // change state based on ruleset and living neighbors
        int alive_neighbors = 0;
        foreach (Tile neighbor in _neighbors)
        {
            if (neighbor._state) alive_neighbors += 1;
        }

        if (!_state)
        {
            if (_board._mode[0].Contains(alive_neighbors))
            {
                _newState = true;
                _board._livingCells += 1;
            }
            else
            {
                _newState = false;
            }
        }
        else
        {
            if (_board._mode[1].Contains(alive_neighbors))
            {
                _newState = true;
            }
            else
            {
                _newState = false;
                _board._livingCells -= 1;
            }
        }
    }
}

class Program
{
    static void Main(string[] args)
    {
        Console.Write("Running the program :)");
        Board board = new Board(new Vector2(10, 10), new Vector2(100, 100));
        board.Populate(PopType.Percentage, percentage: 0.3f);
    }
}

public enum PopType
{
    Percentage,
    Checkerboard,
    Lines,
    Edges
}

static class RandomExtensions
{
    public static void Shuffle<T> (this Random rng, T[] array)
    {
        int n = array.Length;
        while (n > 1) 
        {
            int k = rng.Next(n--);
            T temp = array[n];
            array[n] = array[k];
            array[k] = temp;
        }
    }
}