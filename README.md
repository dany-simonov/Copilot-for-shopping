Проект: Copilot для шопинга - Ассистент-стилист на основе AI для Wildberries
Описание проекта:

Данный проект представляет собой реализацию “Шопинг-ассистента”, а именно, “Ассистента-стилиста”. Цель проекта - создать интеллектуального помощника, который помогает пользователям находить подходящую одежду и создавать стильные образы, снижая когнитивную нагрузку при выборе и экономя время на онлайн-шопинге.

Проблематика:

Современный онлайн-шопинг характеризуется огромным выбором товаров и перегруженностью информацией. Пользователи сталкиваются с проблемами:

Накрученные отзывы и некачественные фотографии товаров.
Непонятное ценообразование и недоверие к скидкам.
Сложность поиска товаров по жестким фильтрам.
Необходимость тратить много времени на изучение карточек товаров и принятие решений.
Решение:

Наш Shopping Assistant призван решить эти проблемы, предоставляя пользователю персонализированные рекомендации и помогая создавать стильные образы на основе его предпочтений и потребностей.

Целевая аудитория:

Люди, которые ценят свое время, интересуются модой и часто заказывают одежду онлайн, но хотят сделать свой опыт онлайн-шопинга более “умным” и эффективным.

Функциональность:

Ассистент-стилист реализован в виде Telegram-бота и обладает следующими возможностями:

Определение потребностей пользователя:
Бот задает пользователю вопросы о поле, типе мероприятия, желаемом стиле, бюджете, предпочтениях по цвету, размере одежды и обуви, а также о дополнительных пожеланиях.
Составление оптимального набора товаров:
На основе полученных ответов бот формирует поисковые запросы для Wildberries.
Используется библиотека g4f для генерации релевантных поисковых запросов на основе пользовательских данных.
В связи с невозможностью получения доступа к официальному API Wildberries, был реализован парсинг сайта.
Представление результатов:
Бот возвращает пользователю список поисковых запросов, которые можно использовать для поиска товаров на Wildberries.
Поддержка обратной связи:
Бот может задавать уточняющие вопросы и корректировать результаты на основе комментариев пользователя.
Использованные технологии:

Python: Основной язык программирования.
pyTelegramBotAPI: Библиотека для работы с Telegram Bot API.
g4f: Библиотека для работы с нейросетями (генерация текста).
requests и BeautifulSoup4: Библиотеки для парсинга веб-страниц.

Дальнейшее развитие:

Интеграция с другими маркетплейсами: Добавить поддержку других маркетплейсов (Lamoda, Ozon, Яндекс маркет).
Улучшение UI: Сделать UI бота более привлекательным и удобным.
Реализация ML для рекомендаций: Внедрить ML-модели для более точной персонализации рекомендаций.
Развертывание на сервере: Развернуть бота на сервере для обеспечения постоянной доступности.
Добавление новых “скиллов”: Реализовать другие “скиллы” ассистента (например, ассистент-косметолог, ассистент-дизайнер).
