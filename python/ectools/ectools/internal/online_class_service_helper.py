from urllib.parse import urljoin

import requests

from ectools.config import config

AXIS_API_TOKEN = {
    'UAT': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEsI" +
           "mlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqd" +
           "GkiOiJhMjE1NTNkZTAzNzI0OTQxOTU4NTlhYmI0ZDRlMjY5MCIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlb" +
           "WFpbCI6ImZyZXNobWVhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZ" +
           "XhwIjoyNTM0MDIzMDA3OTksImlhdCI6MTUzMjY3MTMzOH0.Mk7UndCv-M6usXSOsXWjT24uEShTl_w9h" +
           "Rmj60TM4svlx5GRMNiGc-1DOva29OqU1MhRuOgJLAz71E2v3fFu5aW8TvkREmJ8XnZOmYHDpNqvEYxOa" +
           "lpTEd4Og4nVKaAirOQbtyGiHeOYi-cE6Lp6AaJE4y5aqCgAjmwyr5q5WnU",
    'UATCN': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEsI" +
             "mlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqd" +
             "GkiOiJhMjE1NTNkZTAzNzI0OTQxOTU4NTlhYmI0ZDRlMjY5MCIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlb" +
             "WFpbCI6ImZyZXNobWVhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZ" +
             "XhwIjoyNTM0MDIzMDA3OTksImlhdCI6MTUzMjY3MTMzOH0.Mk7UndCv-M6usXSOsXWjT24uEShTl_w9h" +
             "Rmj60TM4svlx5GRMNiGc-1DOva29OqU1MhRuOgJLAz71E2v3fFu5aW8TvkREmJ8XnZOmYHDpNqvEYxOa" +
             "lpTEd4Og4nVKaAirOQbtyGiHeOYi-cE6Lp6AaJE4y5aqCgAjmwyr5q5WnU",
    'QA': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEs" +
          "ImlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqdGki" +
          "OiIxZTE5YmY5M2U4NmY0NDk1OGNlNDljMGQ0NWI2MmNkMCIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlbWFpbCI6I" +
          "mZyZXNobWVhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZXhwIjoyNTM0MD" +
          "IzMDA3OTksImlhdCI6MTUzMjY3MjM0MH0.u3su1QekuCK-Q70vcmW1-MLqUZG-tPgZSAznBWSG0-PIlepNteBi" +
          "QEjKWH1hBNGLXUTnIQwEJTWrvUkxWSpOBSB2AabOHO5KhAjUM1qF00wC5FRNRHdtKGwxISYSpwWY-bR7mE95RMJ" +
          "jjZm-5vq6RxtHnIp8ASkeSDdoSZAPAdI",
    'QACN': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEs" +
            "ImlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqdGki" +
            "OiIxZTE5YmY5M2U4NmY0NDk1OGNlNDljMGQ0NWI2MmNkMCIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlbWFpbCI6I" +
            "mZyZXNobWVhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZXhwIjoyNTM0MD" +
            "IzMDA3OTksImlhdCI6MTUzMjY3MjM0MH0.u3su1QekuCK-Q70vcmW1-MLqUZG-tPgZSAznBWSG0-PIlepNteBi" +
            "QEjKWH1hBNGLXUTnIQwEJTWrvUkxWSpOBSB2AabOHO5KhAjUM1qF00wC5FRNRHdtKGwxISYSpwWY-bR7mE95RMJ" +
            "jjZm-5vq6RxtHnIp8ASkeSDdoSZAPAdI",
    'Staging': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEs" +
               "ImlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqdGkiOiI4O" +
               "WZmMGVlYjZhZTY0NDUzYjMwM2I5NDdiYjc0YjQ2NyIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlbWFpbCI6ImZyZXNobW" +
               "VhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZXhwIjoyNTM0MDIzMDA3OTksIml" +
               "hdCI6MTUzMjY3MjIxMH0.sZBGgKc-ZTwZVI4A_eTRpXlfzzpHBJ3cCCZ1BbiwjDbT4O_pg59_1q3m2jQJUt4c4DAwx" +
               "hwdv_RjMdxPt_MwBCrU1bZ1vD-FYHplUZJsySssAvVH2VU7-61mKshsrocc5tdcNgN8CcfedXkQk9w0aafr7OCZdjF" +
               "znSRBjmo9V20",
    'StagingCN': "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtleXMvcHVibGljL2F4aXMvYXhpcy5wZW0ifQ.eyJzdWIiOjEs" +
                 "ImlzcyI6ImF4aXMuZW5nbGlzaHRvd24uY29tIiwiYXVkIjoiYXhpcy5lbmdsaXNodG93bi5jb20iLCJqdGkiOiI4O" +
                 "WZmMGVlYjZhZTY0NDUzYjMwM2I5NDdiYjc0YjQ2NyIsIm5hbWUiOiJmcmVzaG1lYXQiLCJlbWFpbCI6ImZyZXNobW" +
                 "VhdEBxcDEub3JnIiwiZ2VuZGVyIjoiTSIsInJvbGUiOiJTdXBlckFkbWluIiwiZXhwIjoyNTM0MDIzMDA3OTksIml" +
                 "hdCI6MTUzMjY3MjIxMH0.sZBGgKc-ZTwZVI4A_eTRpXlfzzpHBJ3cCCZ1BbiwjDbT4O_pg59_1q3m2jQJUt4c4DAwx" +
                 "hwdv_RjMdxPt_MwBCrU1bZ1vD-FYHplUZJsySssAvVH2VU7-61mKshsrocc5tdcNgN8CcfedXkQk9w0aafr7OCZdjF" +
                 "znSRBjmo9V20"
}


def get_axis_root():
    return config.axis_root


def get_axis_token():
    return AXIS_API_TOKEN[config.env]


class JwtAuthWebRequest:
    def __init__(self, base_url: str, token: str):
        self._session = requests.session()
        self._session.verify = False
        self._session.headers["Authorization"] = "Bearer " + token
        self._base_url = base_url

    def post(self, url: str, data=None, json=None, **kwargs):
        return self._session.post(url=urljoin(self._base_url, url), data=data, json=json, **kwargs)

    def get(self, url: str, params=None, **kwargs):
        return self._session.get(url=urljoin(self._base_url, url), params=params, **kwargs)

    def delete(self, url: str, **kwargs):
        return self._session.delete(url=urljoin(self._base_url, url), **kwargs)

    def put(self, url: str, data=None, **kwargs):
        return self._session.put(url=urljoin(self._base_url, url), data=data, **kwargs)

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class OnlineClassApi(JwtAuthWebRequest):
    def __init__(self, base_url, token):
        super().__init__(base_url, token)

    def get_class_type(self):
        class_type = self.get("/axis/api/v2/classtype").json()
        return class_type

    def allocate_class(self, params):
        """
        params = {
          "classes": [
            {
              "allocationClassTypes": [
                {
                  "serviceType": "PL",
                  "serviceSubType": "Unspecific",
                  "level": "Any",
                  "partner": "Any",
                  "market": "Any",
                  "language": "en",
                  "teachingItem": "en",
                  "evcServer": "EvcCN1",
                  "duration": "60"
                }
              ],
              "startTime": "2020-03-04T11:00:00Z",
              "endTime": "2020-03-04T12:00:00Z",
              "centerCode": "FWW",
              "sourceTypeCode": "Allocated"
            }
          ],
          "operator": {
            "operatedBy": "AxisTool",
            "operatorType": "AxisTool"
          }
        }
        """
        response = self.post("/axis/api/v2/qa/class", json=params)
        if response.status_code != 200:  # no content
            raise Exception(
                "Request failed, status code: %s, content: %s" % (response.status_code, response.content.decode()))
        return response.json()

    def set_availability(self, params):
        """
        params = {
          "timeRange": {
            "startTime": "2020-03-04T11:00:00Z",
            "endTime": "2020-03-04T12:00:00Z"
          },
          "teacherCriteria": {
            "teacherMemberId": 10708789
          },
          "availabilities": [
            {
              "teacherMemberId": 10708789,
              "startTime": "2020-03-04T11:00:00Z",
              "endTime": "2020-03-04T12:00:00Z"
            }
          ]
        }
        """
        response = self.post("/axis/api/v1/availability", json=params)
        if response.status_code != 204:  # no content
            raise Exception(
                "Request failed, status code: %s, content: %s" % (response.status_code, response.content.decode()))

    def assign_class(self, params):
        """
        params = {
          "classId": 123456,
          "teacherMemberId": 456789
        }
        """
        response = self.post("/axis/api/v2/qa/assignclass", json=params)
        if response.status_code != 204:  # no content
            raise Exception(
                "Request failed, status code: %s, content: %s" % (response.status_code, response.content.decode()))
