// Динамическое отслеживание ориентации для всех страниц
// Эта функция проверяет соотношение ширины и высоты окна браузера
// и добавляет соответствующий класс к контейнеру для адаптивного дизайна
function updateOrientation() {
    // Получаем элемент контейнера по ID
    const container = document.getElementById('container');
    // Получаем текущую ширину и высоту окна
    const width = window.innerWidth;
    const height = window.innerHeight;
    // Если ширина больше 1.2 раза высоты, считаем ориентацию горизонтальной
    if (width > 1.2 * height) {
        // Добавляем класс 'horizontal' и удаляем 'vertical'
        container.classList.add('horizontal');
        container.classList.remove('vertical');
    } else {
        // Иначе, добавляем 'vertical' и удаляем 'horizontal'
        container.classList.add('vertical');
        container.classList.remove('horizontal');
    }
}

// Инициализация при загрузке DOM (страницы)
document.addEventListener('DOMContentLoaded', function() {
    // Вызываем функцию обновления ориентации сразу после загрузки
    updateOrientation();
    // Добавляем слушатель события изменения размера окна для динамического обновления
    window.addEventListener('resize', updateOrientation);

    // Код для страницы поиска (AJAX-функционал)
    // Проверяем, существует ли форма поиска на странице
    const searchPage = document.getElementById('searchForm');
    if (searchPage) {
        // Получаем элементы: поле ввода, кнопку и контейнер для результатов
        const input = document.getElementById('searchInput');
        const btn = document.getElementById('searchBtn');
        const resultsDiv = document.getElementById('results');

        // Функция выполнения поиска
        function performSearch() {
            // Получаем значение из поля ввода
            const query = input.value;
            // Отправляем POST-запрос на серверный маршрут /search_results
            // с JSON-телом, содержащим поисковый запрос
            // Заголовок указывает на JSON с кодировкой UTF-8 для поддержки русских символов
            fetch('/search_results', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json; charset=utf-8' },  // Обратите внимание: в оригинале был лишний символ ', исправлено на правильный заголовок
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())  // Парсим ответ как JSON
            .then(employees => {
                // Очищаем контейнер результатов
                resultsDiv.innerHTML = '';
                // Если результатов нет, показываем сообщение
                if (employees.length === 0) {
                    resultsDiv.innerHTML = '<p>Ничего не найдено.</p>';
                    return;
                }
                // Для каждого сотрудника создаем HTML-элемент и добавляем в результаты
                employees.forEach(emp => {
                    const div = document.createElement('div');
                    div.className = 'employee';  // Добавляем класс для стилизации
                    div.innerHTML = `
                        <strong>${emp.name}</strong> - ${emp.position}<br>
                        Отдел: ${emp.department}, Город: ${emp.city}
                    `;
                    resultsDiv.appendChild(div);
                });
            })
            .catch(error => console.error('Ошибка поиска:', error));  // Логируем ошибки в консоль
        }

        // Добавляем слушатель клика на кнопку для выполнения поиска
        btn.addEventListener('click', performSearch);
        // Добавляем слушатель нажатия клавиши Enter в поле ввода для выполнения поиска
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    }
});
