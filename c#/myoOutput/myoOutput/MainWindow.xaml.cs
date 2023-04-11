using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

using ZedGraph;

using MyoSharp.Communication;
using MyoSharp.Device;

namespace myoOutput
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private const int NUMBER_OF_SENSORS = 8;

        private static readonly Color[] DATA_SERIES_COLORS = new Color[]
        
            Color.Red,
            Color.Blue,
            Color.Green,
            Color.Yellow,
            Color.Pink,
            Color.Orange,
            Color.Purple,
            Color.Black,
        };

        public MainWindow()
        {
            InitializeComponent();
        }
    }
}
