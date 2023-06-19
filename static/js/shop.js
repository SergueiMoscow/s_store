function makeRequest(url, method, data={}, callback) {
  let requestOptions = {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    }
  };

  if (method === 'GET') {
    const params = new URLSearchParams(data);
    url += '?' + params;
  } else {
    requestOptions.body = JSON.stringify(data);
  }

  fetch(url, requestOptions)
//    .then(response => response.json())
    .then(response => response.text())
    .then(result => callback(result))
    .catch(error => console.error(error));
}

const changeCategory = (event) => {
    let categoryId = 0;
    if (typeof(event) == 'object' && document.querySelector("#select_categories")) {
        categoryId = event.target.value;
    } else if (typeof(event) == 'number') {
        categoryId = event;
    }
    if (categoryId == 0) {
        window.location.replace('/');
    } else {
        categories.forEach(el => {
            if (el.id == categoryId) {
                makeRequest(el.url, 'GET', {}, function(data){
                    document.getElementById('right').innerHTML = data;
                });
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector("#select_categories")) {
        document.querySelector("#select_categories").addEventListener('change', changeCategory);
    }
});