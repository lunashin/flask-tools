

function init()
{
    // change イベントハンドラ登録

    // Base64エンコード
    elem = document.getElementById("csv-input");
    elem.addEventListener('change', (event) => {
        // alert(event.target.value);

        // 列番号取得
        column_task_num = -1
        column_days_num = -1
        column_role_num = -1

        let column_task = document.getElementById("column-task").value;
        if (column_task != '') {
          column_task_num = Number(column_task)
        }
        let column_days = document.getElementById("column-days").value;
        if (column_days != '') {
          column_days_num = Number(column_days)
        }
        let column_role = document.getElementById("column-role").value;
        if (column_role != '') {
          column_role_num = Number(column_role)
        }

        // POST
        postData("/csv",  { data: event.target.value, column_task: column_task_num, column_days: column_days_num, column_role: column_role_num })
        .then(data => {
            elem = document.getElementById("csv-result");
            elem.value = data.result;
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
