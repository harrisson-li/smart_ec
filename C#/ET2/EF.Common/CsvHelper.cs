using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CSV = CsvHelper;

namespace EF.Common
{
    public static class CsvHelper
    {
        /// <summary>
        /// Load CSV file to a data table.
        /// </summary>
        /// <param name="csvFile">The csv file.</param>
        /// <returns></returns>
        public static DataTable LoadDataFromCsv(string csvFile)
        {
            using (TextReader reader = File.OpenText(csvFile))
            {
                var csv = new CSV.CsvReader(reader);
                csv.ReadHeader();
                var headers = csv.FieldHeaders.ToList();
                var table = BuildTableWithHeaders(headers);
                while (csv.Read())
                {
                    table.Rows.Add(csv.CurrentRecord);
                }

                return table;
            }
        }

        private static DataTable BuildTableWithHeaders(List<string> listOfHeaders)
        {
            var table = new DataTable();
            foreach (string header in listOfHeaders)
            {
                table.Columns.Add(header, typeof(string));
            }
            return table;
        }
    }
}