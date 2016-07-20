using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ET2.Models
{
    public enum ActionTypes
    {
        Cmd,
        Url
    }

    public class ActionParameters
    {
        public string Name { get; set; }

        public ActionTypes ActionType { get; set; }

        public string Parameter { get; set; }
    }
}