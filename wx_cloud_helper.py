import urllib.parse
import urllib.request
import json
import os
import math
import sys
import copy
import datetime
import requests

class WXDatabaseHelper:
    GET_ACCESS_TOKEN_API = "https://api.weixin.qq.com/cgi-bin/token?"
    CREATE_QRCODE_API = "https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?"
    UPLOAD_FILE_API = "https://api.weixin.qq.com/tcb/uploadfile?"
    DOWNLOAD_FILE_API = "https://api.weixin.qq.com/tcb/batchdownloadfile?"
    DELETE_FILE_API = "https://api.weixin.qq.com/tcb/batchdeletefile?"
    IMPORT_DATABASE_API = "https://api.weixin.qq.com/tcb/databasemigrateimport?"
    EXPORT_DATABASE_API = "https://api.weixin.qq.com/tcb/databasemigrateexport?"
    QUERY_INFO_DATABASE_API = "https://api.weixin.qq.com/tcb/databasemigratequeryinfo?"
    GET_COLLECTION_INFO_API = "https://api.weixin.qq.com/tcb/databasecollectionget?"
    CREATE_COLLECTION_API = "https://api.weixin.qq.com/tcb/databasecollectionadd?"
    DELETE_COLLECTION_API = "https://api.weixin.qq.com/tcb/databasecollectiondelete?"
    ADD_DOCUMENT_API = "https://api.weixin.qq.com/tcb/databaseadd?"
    UPDATE_DOCUMENT_API = "https://api.weixin.qq.com/tcb/databaseupdate?"
    DELETE_DOCUMENT_API = "https://api.weixin.qq.com/tcb/databasedelete?"
    QUERY_DOCUMENT_API = "https://api.weixin.qq.com/tcb/databasequery?"
    COUNT_DOCUMENT_API = "https://api.weixin.qq.com/tcb/databasecount?"
    INVOKE_CLOUND_FUNCTION_API = "https://api.weixin.qq.com/tcb/invokecloudfunction?"

    def __init__(self, app_id, secret_key, server_env):
        self.app_id = app_id
        self.secret_key = secret_key
        self.server_env = server_env
        self.get_access_token()

    @property
    def headers(self):
        return {"Content-Type": "application/json; charset=utf-8"}

    def get_access_token(self):
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.secret_key,
        }
        query = urllib.parse.urlencode(params)
        resp = urllib.request.urlopen(self.GET_ACCESS_TOKEN_API + query)
        json_str = resp.read().decode("utf-8")
        ret_obj = json.loads(json_str)
        if "errcode" in ret_obj and ret_obj["errcode"] == 0:
            print("Error : ", ret_obj["errcode"], ret_obj["errmsg"])
            self.access_token = ""
        else:
            self.access_token = ret_obj["access_token"]

    def create_qrcode(self, path, width=None):
        data = {"access_token": self.access_token, "path": path, "width": width}
        data = json.dumps(data).encode("utf-8")
        url = self.CREATE_QRCODE_API + "ACCESS_TOKEN=" + self.access_token
        req = urllib.request.Request(url, data=data, headers=self.headers)
        resp = urllib.request.urlopen(req)

        with open("qrcode.jpg", "wb") as f:
            self.qrcode_bytes = resp.read()
            f.write(self.qrcode_bytes)
    
    def upload_file(self, path):
        data = {
            "env": self.server_env,
            "path": path
        }
        url = self.UPLOAD_FILE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        upload_success = self._upload_real_file(path, ret_obj)
        return upload_success, ret_obj

    def _upload_real_file(self, path, data):
        files = {
            "file":open(path,"rb")
        }
        param = {
            "enctype":"multipart/form-data",
            "key": path,
            "Signature": data["authorization"],
            "x-cos-security-token":data["token"],
            "x-cos-meta-fileid":data["cos_file_id"]
        }
        reponse = requests.post(data["url"], data=param, files=files)
        return reponse.status_code == 204

    # def _upload_real_file(self, path, data):
    #     f = open(path, "rb")
    #     # headers = copy.deepcopy(self.headers)
    #     # headers.update({'Content-Type':"multipart/form-data"})
    #     param = {
    #         "key": path,
    #         "Signature": data["authorization"],
    #         "x-cos-security-token":data["token"],
    #         "x-cos-meta-fileid":data["cos_file_id"],
    #         "file": "11111111111111",
    #         "Content-Type":"multipart/form-data"
    #     }
    #     # self._send_request(param, data["url"], headers)
    #     param = json.dumps(param).encode("utf-8")
    #     req = urllib.request.Request(data["url"], data=param, headers=self.headers)
    #     resp = urllib.request.urlopen(req)
    #     json_str = resp.read().decode("utf-8")
    #     f.close()
    #     print(json_str)

    def download_file(self, file_list):
        data = {
            "env": self.server_env,
            "file_list": file_list
        }
        url = self.DOWNLOAD_FILE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def delete_file(self, fileid_list):
        data = {
            "env": self.server_env,
            "fileid_list": fileid_list
        }
        url = self.DELETE_FILE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def import_database(self, collection_name, file_path, file_type = 1, stop_on_error = True, conflict_mode = 1):
        data = {
            "env": self.server_env,
            "collection_name": collection_name,
            "file_path": file_path,
            "file_type": file_type,
            "stop_on_error": stop_on_error,
            "conflict_mode": conflict_mode
        }
        url = self.IMPORT_DATABASE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def export_database(self, collection_name, condition,
                        file_path, file_type = 1, 
                        conflict_mode = 1):
        prefix = "db.collection('" + collection_name + "').where("
        middle = ")"
        suffix = ".get()"
        query = prefix + self._encode_str(condition) + middle + suffix
        data = {
            "env": self.server_env,
            "file_path": file_path,
            "file_type": file_type,
            "query": query
        }
        url = self.EXPORT_DATABASE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def query_info_database(self, job_id):
        data = {
            "env": self.server_env,
            "job_id": job_id
        }
        url = self.QUERY_INFO_DATABASE_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def get_collection_info(self, limit = None, offset = None):
        data = {
            "env": self.server_env,
            "limit": limit,
            "offset": offset
        }
        url = self.GET_COLLECTION_INFO_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def create_collection(self, collection_name):
        data = {
            "env": self.server_env, 
            "collection_name": collection_name
        }
        url = self.CREATE_COLLECTION_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def delete_collection(self, collection_name):
        data = {
            "env": self.server_env, 
            "collection_name": collection_name
        }
        url = self.DELETE_COLLECTION_API + "ACCESS_TOKEN=" + self.access_token
        ret_obj = self._send_request(data, url)
        return ret_obj

    def add_document(self, collection_name, document):
        prefix = "db.collection('" + collection_name + "').add({data:"
        suffix = "})"
        query = prefix + self._encode_str(document) + suffix
        # print(query)
        url = self.ADD_DOCUMENT_API + "ACCESS_TOKEN=" + self.access_token
        return self._document_action(query, url)

    def update_document(self, collection_name, condition, document):
        prefix = "db.collection('" + collection_name + "').where("
        middle = ").update({data:"
        suffix = "})"
        query = prefix + self._encode_str(condition) + middle + self._encode_str(document) + suffix
        url = self.UPDATE_DOCUMENT_API + "ACCESS_TOKEN=" + self.access_token
        return self._document_action(query, url)

    def delete_document(self, collection_name, condition = None):
        prefix = "db.collection('" + collection_name + "').where("
        suffix = ").remove()"
        if(condition):
            middle = self._encode_str(condition)
        else:
            middle = '{_id: _.neq("")}'
        query = prefix + middle + suffix
        url = self.DELETE_DOCUMENT_API + "ACCESS_TOKEN=" + self.access_token
        return self._document_action(query, url)

    def count_document(self, collection_name, condition = None):
        prefix = "db.collection('" + collection_name + "').where("
        suffix = ").count()"
        if(condition):
            middle = self._encode_str(condition)
        else:
            middle = '{_id: _.neq("")}'
        query = prefix + middle + suffix
        url = self.COUNT_DOCUMENT_API + "ACCESS_TOKEN=" + self.access_token
        return self._document_action(query, url)

    def query_document(self, collection_name, condition, field = None, orderby = None, limit = None, skip = None):
        prefix = "db.collection('" + collection_name + "').where("
        middle1 = ")"
        middle2 = ".field("
        middle3 = ")"

        suffix = ".get()"
        orderby_q = ".orderBy('" + orderby[0] + "','" + orderby[1] + "')" if orderby else ""
        limit_q = ".limit(" + str(limit) + ")" if limit else ""
        skip_q  = ".skip(" + str(skip) + ")" if skip else "" 
        
        if(condition):
            middle = self._encode_str(condition)
        else:
            middle = '{_id: _.neq("")}'

        if(field):
            middle += middle1 + middle2 + self._encode_str(field)
        query = prefix + middle + middle3 + orderby_q + limit_q + skip_q + suffix
        print(query)
        url = self.QUERY_DOCUMENT_API + "ACCESS_TOKEN=" + self.access_token
        return self._document_action(query, url)

    def invoke_clound_function(self, name, params):
        data = {
            "access_token": self.access_token,
            "env": self.server_env, 
            "name": name
        }
        url = self.INVOKE_CLOUND_FUNCTION_API + urllib.parse.urlencode(data)
        return self._document_action(params, url)

    def _document_action(self, query, url):
        data = {
            "env": self.server_env, 
            "query": query
        }
        ret_obj = self._send_request(data, url)
        return ret_obj

    def _send_request(self, data, url, headers = None):
        try:
            headers = headers or self.headers
            data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers)
            resp = urllib.request.urlopen(req)
            json_str = resp.read().decode("utf-8")
            print(json_str)
            ret_obj = json.loads(json_str)
        except:
            ret_obj = {}
        return ret_obj

    def _encode_str(self, value):
        if type(value) == dict:
            obj_str = "{"
            for k, v in value.items():
                obj_str += k
                obj_str += ":"
                obj_str += self._encode_str(v)
                obj_str += ","
            obj_str = obj_str[:-1]
            obj_str += "}"
            return obj_str
        elif type(value) == int:
            return str(value)
        elif type(value) == str:
            return "'" + value + "'"
        elif type(value) == list:
            obj_str = "["
            for l in value:
                obj_str += self._encode_str(l)
                obj_str += ","
            obj_str = obj_str[:-1]
            obj_str += "]"
            return obj_str
        elif type(value) == bool:
            return "true" if value else "false"
        elif type(value) == datetime.datetime:
            return 'new Date("' + value.isoformat() + "Z" + '")'
        else:
            try:
                return "'" + str(value) + "'"
            except:
                return "'<<WrongTypeData>>'"


