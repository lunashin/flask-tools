

function init()
{
    // change イベントハンドラ登録

    // Base64エンコード
    elem = document.getElementById("base64encode_from");
    elem.addEventListener('change', (event) => {
        // alert(event.target.value);

        // POST
        postData("/b64encode",  { data: event.target.value })
        .then(data => {
            elem = document.getElementById("base64encode_result");
            elem.value = data.result;
        });
    });

    // Base64デコード
    elem = document.getElementById("base64decode_from");
    elem.addEventListener('change', (event) => {
        // alert(event.target.value);

        // POST
        postData("/b64decode",  { data: event.target.value })
        .then(data => {
            elem = document.getElementById("base64decode_result");
            elem.value = data.result;

            elem = document.getElementById("base64decode_json");
            elem.value = data.json_formated;
          });
    });

    // Base64デコード
    elem = document.getElementById("json_format_from");
    elem.addEventListener('change', (event) => {
        // alert(event.target.value);

        // POST
        postData("/json_format",  { data: event.target.value })
        .then(data => {
            elem = document.getElementById("json_format_result");
            elem.value = data.result;

            elem = document.getElementById("json_format_json");
            elem.value = data.json_formated;
          });
    });

}


// POST
async function postData(url = '', data = {}) {
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // 本文のデータ型は "Content-Type" ヘッダーと一致させる必要があります
  })
  return response.json(); // JSON のレスポンスをネイティブの JavaScript オブジェクトに解釈
}


init()
