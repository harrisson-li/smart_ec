using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace EF.Common
{
    /// <summary>
    /// This module implements data generators for various distributions.
    ///
    /// Provide low level random data: --------- Numbers, string, date, bool, hash etc.
    ///
    /// Provide sequences random: --------- Pick random element Pick random sample Generate random permutation
    /// </summary>
    public class RandomProvider
    {
        #region Source

        private static Random mRand;

        internal static Random Rand
        {
            get
            {
                if (mRand == null)
                {
                    mRand = new Random();
                }
                return mRand;
            }
        }

        public static string Numbers = "0123456789";
        public static string Hex = Numbers + "abcedf";
        public static string Letters = "abcdefghijklmnopqrstuvwxyz";
        public static string Symbols = ",.;:?!/\\@#$%^&()=+*-_{}[]<>|~";

        #endregion Source

        #region Numbers

        /// <summary>
        /// Return a random integer N in the range [min, max], including min, max.
        /// </summary>
        /// <param name="min">The min value.</param>
        /// <param name="max">The max value.</param>
        public static int GetInteger(int min, int max)
        {
            if (min > max)
            {
                throw new ArgumentOutOfRangeException("The min could not be greater than max!");
            }
            return min + Rand.Next(max - min + 1);
        }

        /// <summary>
        /// Return a random integer in the range [0, max], including max.
        /// </summary>
        /// <param name="max">The max value.</param>
        public static int GetInteger(int max)
        {
            if (max < 0)
            {
                throw new ArgumentOutOfRangeException("The max must larger than 0!");
            }
            return GetInteger(0, max);
        }

        /// <summary>
        /// Returns a specific length of number. e.g. Card No.
        /// </summary>
        /// <param name="length">The length of number.</param>
        public static string GetNumber(int length)
        {
            if (length < 1)
            {
                throw new ArgumentOutOfRangeException("The length must larger than 0!");
            }
            return new string((Sample(Numbers.ToArray(), length)).ToArray());
        }

        /// <summary>
        /// Returns a double number, use for percentage or money value.
        /// </summary>
        /// <param name="min">The min value.</param>
        /// <param name="max">The max value.</param>
        /// <param name="decimals">The decimals.</param>
        public static double GetDouble(double min, double max, int decimals = 2)
        {
            if (min > max)
            {
                throw new ArgumentOutOfRangeException("The min could not be greater than max!");
            }
            double result = min + Rand.NextDouble() * (max - min);
            return Math.Round(result, decimals);
        }

        #endregion Numbers

        #region Strings

        /// <summary>
        /// Gets a random string.
        /// </summary>
        /// <param name="minLength">Min length of the string.</param>
        /// <param name="maxLength">Max length of the string.</param>
        public static string GetString(int minLength = 3, int maxLength = 12)
        {
            // We should get clear out later what kind of chars should be produced here

            var pool = (Letters + Letters.ToUpper()).ToArray();
            return GetString(minLength, maxLength, pool);
        }

        /// <summary>
        /// Gets a random string with numbers.
        /// </summary>
        /// <param name="minLength">Min length of the string.</param>
        /// <param name="maxLength">Max length of the string.</param>
        public static string GetStringWithNumber(int minLength = 3, int maxLength = 12)
        {
            // We should get clear out later what kind of chars should be produced here

            var pool = (Numbers + Letters + Letters.ToUpper()).ToArray();
            return GetString(minLength, maxLength, pool);
        }

        /// <summary>
        /// Gets a random string with symbol and numbers.
        /// </summary>
        /// <param name="minLength">Min length of the string.</param>
        /// <param name="maxLength">Max length of the string.</param>
        public static string GetStringWithSymbol(int minLength = 3, int maxLength = 12)
        {
            // Get random string from common chars, it might not fit for real tests We should get clear
            // out later what kind of chars should be produced here

            var pool = (Numbers + Letters + Letters.ToUpper() + Symbols).ToArray();
            return GetString(minLength, maxLength, pool);
        }

        /// <summary>
        /// Get a random string from specific char pool.
        /// </summary>
        /// <param name="minLength">The min length of out string.</param>
        /// <param name="maxLength">The max length of out string.</param>
        /// <param name="pool">The char pool.</param>
        public static string GetString(int minLength, int maxLength, char[] pool)
        {
            if (minLength > maxLength)
            {
                throw new ArgumentOutOfRangeException("The minLength could not be greater than maxLength!");
            }

            if (pool == null || pool.Length == 0)
            {
                throw new ArgumentNullException("The char pool should not be empty!");
            }

            var len = GetInteger(minLength, maxLength);
            var ret = Sample(pool, len);
            return new string(ret.ToArray());
        }

        /// <summary>
        /// Makes a string fuzzed.
        /// </summary>
        /// <param name="input">The input string.</param>
        /// <param name="level">
        /// The fuzz level. 1 - Just reorder chars in string. 2 - Fuzz string with number and letter,
        /// length will not be changed. 3 - Fuzz string with number, letter and symbols, length might be changed.
        /// </param>
        /// <returns>The fuzzed string.</returns>
        public static string FuzzString(string input, int level = 1)
        {
            var pool = input;
            var min = input.Length;
            var max = input.Length;
            var cur = input.Length;

            switch (level)
            {
                case 1:
                    // Lv1: Default fuzz rule, just change the string order.
                    break;

                case 2:
                    // Lv2: Add numbers and letter to fuzz, length was not changed.
                    pool = input + Numbers + Letters;
                    break;

                case 3:
                    // Lv3: Add all chars to fuzz, might change the length as well.
                    pool = input + Numbers + Letters + Letters.ToUpper() + Symbols;
                    min = GetInteger(cur);
                    max = GetInteger(cur * GetInteger(cur));
                    break;

                default:
                    throw new ArgumentException("Incorrect fuzz level, must in range [1-3]!");
            }

            var len = GetInteger(min, max);
            return new string(Sample(pool.ToArray(), len, false).ToArray());
        }

        #endregion Strings

        #region Other

        /// <summary>
        /// Gets a date in range.
        /// </summary>
        /// <param name="yearsBefore">The years before. default to 50</param>
        /// <param name="yearsAfter">The years after. default to 50</param>
        public static DateTime GetDate(int yearsBefore = 50, int yearsAfter = 50)
        {
            if (yearsAfter + yearsBefore <= 0)
            {
                throw new ArgumentOutOfRangeException("No date could get from the specific range!");
            }

            var earlyDate = DateTime.Today.AddYears(-yearsBefore);
            var laterDate = DateTime.Today.AddYears(yearsAfter);

            int range = (int)(laterDate - earlyDate).TotalDays;
            return earlyDate.AddDays(Rand.Next(range));
        }

        /// <summary>
        /// Gets a Boolean value.
        /// </summary>
        public static bool GetBoolean()
        {
            return Rand.Next(100) > 50;
        }

        /// <summary>
        /// Gets the ticks of current time.
        /// </summary>
        internal static long GetTicks()
        {
            return DateTime.Now.Ticks;
        }

        /// <summary>
        /// Gets a hash value in specific length.
        /// </summary>
        /// <param name="length">The length of hash.</param>
        internal static string GetHash(int length)
        {
            if (length < 1)
            {
                throw new ArgumentOutOfRangeException("The given length must larger than 0!");
            }

            return new string(Sample(Hex.ToArray(), length).ToArray());
        }

        #endregion Other

        #region List/Array

        /// <summary>
        /// Pick a random element from the non-empty sequence.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="seq">The sequence.</param>
        public static T Pick<T>(IEnumerable<T> seq)
        {
            var index = GetInteger(0, seq.Count() - 1);
            return seq.Skip(index).First();
        }

        /// <summary>
        /// Pick a random element from the non-empty sequence.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="seq">The sequence.</param>
        public static T Pick<T>(Array seq)
        {
            return (T)seq.GetValue(Rand.Next(seq.Length));
        }

        /// <summary>
        /// Pick a random element from enum type.
        /// </summary>
        /// <typeparam name="T">The type of enum.</typeparam>
        public static T Pick<T>() where T : struct, IConvertible // Enum constraint
        {
            if (!typeof(T).IsEnum)
            {
                throw new ArgumentException("T ought to be an enum type");
            }

            return Pick<T>(Enum.GetValues(typeof(T)));
        }

        /// <summary>
        /// Picks another element of a sequence, will not handle a sequence with all same elements.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="seq">The sequence.</param>
        /// <param name="current">The current element.</param>
        public static T PickAnother<T>(IEnumerable<T> seq, T current)
        {
            if (seq == null || !seq.Contains(current))
            {
                throw new ArgumentException("The given element does not exist in sequence!");
            }

            var temp = seq.Where(e =>
            {
                return e == null ? !ReferenceEquals(e, current) : !e.Equals(current);
            });

            if (temp.Count() == 0)
            {
                throw new ArgumentException("No any other element found in sequence!");
            }

            return Pick(temp);
        }

        /// <summary>
        /// Picks another element from enum type.
        /// </summary>
        /// <typeparam name="T">Any enum type.</typeparam>
        /// <param name="current">The current element.</param>
        public static T PickAnother<T>(T current) where T : struct, IConvertible // Enum constraint
        {
            if (!typeof(T).IsEnum)
            {
                throw new ArgumentException("T ought to be an enum type.");
            }

            var all = Enum.GetValues(typeof(T)).Cast<T>();
            return PickAnother(all, current);
        }

        /// <summary>
        /// Return a specific length list of unique elements chosen from the population sequence.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="population">The population sequence.</param>
        /// <param name="length">The length of sample to pick.</param>
        /// <param name="allowDuplicate">if set to <c>true</c> [allow duplicate].</param>
        /// <returns>
        /// Returns a new list containing elements from the population while leaving the original
        /// population unchanged
        /// </returns>
        public static List<T> Sample<T>(IEnumerable<T> population, int length, bool allowDuplicate = true)
        {
            if (population == null)
            {
                throw new ArgumentNullException("The given sequence is null!");
            }

            if (length < 1)
            {
                throw new ArgumentOutOfRangeException("The given length must larger than 0!");
            }

            var result = new List<T>();
            var copy = population.ToList();
            T temp;

            for (int i = 0; i < length; ++i)
            {
                if (allowDuplicate)
                {
                    var pickIndex = Rand.Next(copy.Count);
                    result.Add(copy[pickIndex]);
                }
                else
                {
                    // will throw exception if sample count is larger than population self
                    var pickIndex = Rand.Next(copy.Count - i);
                    result.Add(copy[pickIndex]);

                    // move the pick value to the end
                    temp = copy[pickIndex];
                    copy[pickIndex] = copy[copy.Count - 1 - i];
                    copy[copy.Count - 1 - i] = temp;
                }
            }
            return result;
        }

        /// <summary>
        /// Shuffle the sequence, will not change the original sequence.
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="seq">The sequence.</param>
        public static List<T> Shuffle<T>(IEnumerable<T> seq)
        {
            if (seq == null)
            {
                return null;
            }

            var copy = seq.ToList();

            for (int i = 1; i < copy.Count; ++i)
            {
                // Pick a random element to exchange copy[i]
                int j = Rand.Next(copy.Count);

                var tmp = copy[i];
                copy[i] = copy[j];
                copy[j] = tmp;
            }
            return copy;
        }

        #endregion List/Array
    }
}