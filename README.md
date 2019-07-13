# wx-cloud-helper

_a tool for wechat mini program cloud dev_

## Module Usage

```python
# test
helper = WXDatabaseHelper(
    "xxxxxxxxxx", "xxxxxxxxxxxxx", "xxxxx"
)
helper.create_qrcode("pages/index/index", 128)
helper.upload_file("_brand_test1.json")
helper.download_file([
    {
        "fileid":"cloud://xxxxxxxxxx.xxxxxxxx-1259579878/s16.json",
        "max_age":7200
    },
    {
        "fileid":"cloud://xxxxxxxxx.xxxxxxxx-1259579878/_brand_test1.json",
        "max_age":7200
    }
])
helper.delete_file([
    "cloud://xxxxxxxxx.xxxxxxxx-1259579878/s16.json",
    "cloud://xxxxxxxxx.xxxxxxxx-1259579878/_brand_test1.json"
])
helper.create_collection("_brand_test1")
helper.import_database("_brand_test1", "_brand_test1.json")
ret_obj = helper.export_database("_brand_test1", {"hello1":1}, "_brand_test1_export")
helper.query_info_database(ret_obj["job_id"])
helper.get_collection_info()
helper.delete_collection("_brand_test1")
helper.add_document("_brand_test1", {
    "hello1":1,
    "hello2":[1,2,3],
    "hello3":"this is a string",
    "hello4": {
        "a":1,
        "b":[1,2,3],
        "c":"this is a string"
    }
})
helper.count_document("_brand_test1", {"hello1":1})
helper.update_document("_brand_test1", {"hello1":1}, {
    "hello2":[1,2,3,4]
})
helper.delete_document("_brand_test1", {"hello1":1})
helper.invoke_clound_function("getSpecByModelId", {"pid":"s148"})
```