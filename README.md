# Littlelemon API Project
## Description
The Littlelemon API Project is the final assignment for the [APIs Course](https://github.com/adolfojmnz/littlelemon-API/blob/main/README.md#:~:text=assignment%20for%20the-,APIs%20Course,-part%20of%20the) part of the Meta BackEnd Developer Professional Certificate on Coursera.

The API endpoints for this project provide the functionality to create, edit and delete users, roles for each user, such as Customer, Delivery Crew or Manager, menu items, categories for menu items, shopping cart, and orders. Every API endpoint has authorization and permissions constraints as well as throttling, pagination, and filtering.
## Environment and Tools
* OS: MacOS
* Programming Language: Python3
* Database: SQLite3
* API Framework: Django REST framework
* Authentication: Djoser
## Installation
1. Clone the repo.
```bash
git clone https://github.com/CityBoy-Claude/Littlelemon-API-Django.git
```
2. Create the virtual environment and install the dependencies.
```bash
pipenv install
```
## Usage
Run the server by 
```bash
cd Littlelemon && python manage.py runserver
```
## User Group
| ROLE           | GROUP         | RESTRICTION |
| -------------- | ------------- | ----------- |
| Anonymous User | None          | YES         |
| Customer       | Customer      | YES         |
| Delivery Crew  | Delivery crew | YES         |
| Manager        | Manager       | YES         |
| Admin          | SysAdmin      | NO          |
## Database Structure
Defined in the `Littlelemon/LittleLemonAPI/models.py`
### Category
| Field Name | Type    |
| ---------- | ------- |
| id         | Integer |
| title      | Char    |
| slug       | Slug    |
### MenuItem
| Field Name | Type         |
| ---------- | ------------ |
| id         | Integer      |
| title      | Char         |
| price      | Decimal      |
| category   | **Category** |
### Cart
| Field Name | Type         |
| ---------- | ------------ |
| id         | Integer      |
| user       | **User**     |
| menuitem   | **MenuItem** |
| quantity   | SmallInteger |
| unit_price | Decimal      |
| price      | Decimal      |
### Order
| Field Name    | Type     |
| ------------- | -------- |
| id            | Integer  |
| user          | **User** |
| delivery_crew | **User** |
| status        | Boolean  |
| total         | Decimal  |
| data          | Data     |
### OrderItem
| Field Name | Type         |
| ---------- | ------------ |
| id         | Integer      |
| order      | **Order**    |
| menuitem   | **MenuItem** |
| quantity   | SmallInteger |
| unit_price | Decimal      |
| price      | Decimal      |
## Endpoints
Defualt host address: `http://localhost:8000/)`
### User registration and token generation endpoints 
| Endpoint           | Method | Available Group | Purpose                                          |
| ------------------ | ------ | --------------- | ------------------------------------------------ |
| `/users`           | POST   | ALL             | Creates a new user with name, email and password |
| `/users/users/me/` | GET    | ALL             | Displays the current user                        |
| `/token/login/`    | POST   | ALL             | Generates access tokens                          |
### User group management endpoints
| Endpoint                                   | Method | Available Group | Purpose                                                    |
| ------------------------------------------ | ------ | --------------- | ---------------------------------------------------------- |
| `/api/groups/manager/users`                | GET    | Manager         | Returns all managers                                       |
| `/api/groups/manager/users`                | POST   | Manager         | Assigns the user in the payload to the manager group       |
| `/api/groups/manager/users/{userId}`       | DELETE | Manager         | Removes this particular user from the manager group        |
| `/api/groups/delivery-crew/users`          | GET    | Manager         | Returns all delivery crews                                 |
| `/api/groups/delivery-crew/users`          | POST   | Manager         | Assigns the user in the payload to the delivery crew group |
| `/api/groups/delivery-crew/users/{userId}` | DELETE | Manager         | Removes this particular user from the delivery crew group  |
### Menu-items endpoints
| Endpoint                     | Method           | Available Group | Purpose                          |
| ---------------------------- | ---------------- | --------------- | -------------------------------- |
| `/api/menu-items`            | GET              | ALL             | Lists all menu items             |
| `/api/menu-items`            | POST             | Manager         | Creates a new menu item          |
| `/api/menu-items/{menuItem}` | GET              | ALL             | Lists single menu item           |
| `/api/menu-items/{menuItem}` | PUT,PATCH,DELETE | Manager         | Updates/deletes single menu item |
### Cart management endpoints
| Endpoint               | Method | Available Group | Purpose                                              |
| ---------------------- | ------ | --------------- | ---------------------------------------------------- |
| `/api/cart/menu-items` | GET    | Customer        | Lists current items in the cart for the current user |
| `/api/cart/menu-items` | POST   | Customer        | Adds the menu item to the cart                       |
| `/api/cart/menu-items` | DELETE | Customer        | Deletes all menu items created by the current user   |
### Order management endpoints
<style>
table th:nth-of-type(4) {
    width: 10em;
}
</style>
| Endpoint                | Method    | Available Group         | Purpose                                                                                                                                                                                                                     |
| ----------------------- | --------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/orders`           | GET       | Customer, Delivery crew | Returns all orders with order items created by this user or assigned to the delivery crew.                                                                                                                                  |
| `/api/orders`           | GET       | Manager                 | Returns all orders                                                                                                                                                                                                          |
| `/api/orders`           | POST      | Customer                | <div style="width: 300pt">Creates a new order item for the current user. Gets current cart items from the cart endpoints and adds those items to the order items table. Then deletes all items from the cart for this user. |
| `/api/orders/{orderId}` | GET       | Customer                | Returns all items for this order id if the order belongs to the current user                                                                                                                                                |
| `/api/orders/{orderId}` | PUT,PATCH | Delivery crew, Manager  | Update the order. Manager can use it to assign delivery crew. Delivery crew can use it to update the delivery status.                                                                                                       |
| `/api/orders/{orderId}` | DELETE    | Manager                 | Deletes this order                                                                                                                                                                                                          |
### Filtering, searching and ordering
Filtering, searching, and ordering are supported for Menu-items and Order management endpoints.

Example:
Using endpoint `api/menu-items?from_price=5&to_price=10&ordering=price`, get menu items whose price is from 5 to 10, and the results are ordered by price.

### Pagination adn throttling
Pagination and throttling are supported for Menu-items and Order management endpoints. These two functionalities supported by the `Django REST Framework`