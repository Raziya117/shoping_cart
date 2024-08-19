#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define CART_FILENAME "cart.txt"
#define USER_FILENAME "users.txt"
#define MAX_ITEM_NAME 100
#define MAX_ITEMS 100
#define MAX_USERNAME 50
#define MAX_PASSWORD 50
#define MAX_CATEGORIES 4
#define MAX_ITEMS_PER_CATEGORY 10

typedef struct {
    char name[MAX_ITEM_NAME];
    float price; // Price in rupees
} Item;

typedef struct {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];
} User;

typedef struct {
    char name[MAX_ITEM_NAME];
    float price; // Price in rupees
    int quantity;
} CartItem;

void registerUser();
int loginUser();
void displayCategories();
void displayItemsByCategory(int category);
void addItemToCart();
void viewCart();
void saveCartToFile(const char* username);
void loadCartFromFile(const char* username);
void clearCart();
int isPasswordStrong(const char* password);

CartItem cart[MAX_ITEMS];
int itemCount = 0;

// Predefined items categorized with prices in rupees
Item availableItems[MAX_CATEGORIES][MAX_ITEMS_PER_CATEGORY] = {
    // Groceries
    {
        {"Apple", 40.0},
        {"Banana", 20.0},
        {"Orange", 30.0},
        {"Milk", 60.0},
        {"Bread", 50.0},
        {"Eggs", 120.0},
        {"Cheese", 200.0},
        {"Butter", 150.0},
        {"Chicken", 300.0},
        {"Rice", 80.0}
    },
    // Clothes
    {
        {"T-shirt", 1200.0},
        {"Jeans", 3000.0},
        {"Jacket", 4500.0},
        {"Shirt", 1600.0},
        {"Sweater", 2400.0},
        {"Dress", 4000.0},
        {"Shorts", 2000.0},
        {"Skirt", 2800.0},
        {"Hat", 800.0},
        {"Scarf", 960.0}
    },
    // Footwear
    {
        {"Sneakers", 4000.0},
        {"Sandals", 1600.0},
        {"Boots", 5600.0},
        {"Loafers", 3200.0},
        {"Heels", 4800.0},
        {"Slippers", 1200.0},
        {"Running Shoes", 4400.0},
        {"Dress Shoes", 5200.0},
        {"Wedges", 2400.0},
        {"Flip-flops", 800.0}
    },
    // Jewelry
    {
        {"Necklace", 8000.0},
        {"Bracelet", 6400.0},
        {"Ring", 12000.0},
        {"Earrings", 7200.0},
        {"Watch", 16000.0},
        {"Pendant", 5600.0},
        {"Brooch", 4800.0},
        {"Cufflinks", 4000.0},
        {"Anklet", 3200.0},
        {"Charm", 2400.0}
    }
};

int main() {
    int choice;
    int loggedIn = 0;
    char loggedInUser[MAX_USERNAME] = "";

    while (1) {
        printf("\n1. Register\n");
        printf("2. Login\n");
        printf("3. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        getchar(); // Consume newline character

        switch (choice) {
            case 1:
                registerUser();
                break;
            case 2:
                loggedIn = loginUser();
                if (loggedIn) {
                    strcpy(loggedInUser, loggedInUser);
                    break;
                }
            case 3:
                printf("Exiting...\n");
                exit(0);
            default:
                printf("Invalid choice. Please try again.\n");
        }

        if (loggedIn) {
            break;
        }
    }

    loadCartFromFile(loggedInUser);

    while (1) {
        printf("\nShopping Cart Menu:\n");
        printf("1. Add item to cart\n");
        printf("2. View cart\n");
        printf("3. Save and exit\n");
        printf("4. Clear cart\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        getchar();

        switch (choice) {
            case 1:
                displayCategories();
                break;
            case 2:
                viewCart();
                break;
            case 3:
                saveCartToFile(loggedInUser);
                printf("Cart saved. Exiting...\n");
                exit(0);
            case 4:
                clearCart();
                break;
            default:
                printf("Invalid choice. Please try again.\n");
        }
    }

    return 0;
}

void registerUser() {
    User newUser;
    FILE *file = fopen(USER_FILENAME, "a");
    if (file == NULL) {
        perror("Error opening user file");
        exit(1);
    }

    printf("Enter username: ");
    fgets(newUser.username, MAX_USERNAME, stdin);
    newUser.username[strcspn(newUser.username, "\n")] = '\0';

    while (1) {
        printf("Enter password: ");
        fgets(newUser.password, MAX_PASSWORD, stdin);
        newUser.password[strcspn(newUser.password, "\n")] = '\0';

        if (isPasswordStrong(newUser.password)) {
            break;
        } else {
            printf("Password is not strong enough. Please try again.\n");
        }
    }

    fwrite(&newUser, sizeof(User), 1, file);
    fclose(file);
    printf("User registered successfully.\n");
}

int loginUser() {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];
    User user;

    FILE *file = fopen(USER_FILENAME, "r");
    if (file == NULL) {
        perror("Error opening user file");
        return 0;
    }

    printf("Enter username: ");
    fgets(username, MAX_USERNAME, stdin);
    username[strcspn(username, "\n")] = '\0';

    printf("Enter password: ");
    fgets(password, MAX_PASSWORD, stdin);
    password[strcspn(password, "\n")] = '\0';

    while (fread(&user, sizeof(User), 1, file)) {
        if (strcmp(user.username, username) == 0 && strcmp(user.password, password) == 0) {
            printf("Login successful.\n");
            fclose(file);
            return 1;
        }
    }

    fclose(file);
    printf("Invalid username or password. Please try again.\n");
    return 0;
}

void displayCategories() {
    int category;
    printf("\nCategories:\n");
    printf("1. Groceries\n");
    printf("2. Clothes\n");
    printf("3. Footwear\n");
    printf("4. Jewelry\n");
    printf("Enter category number: ");
    scanf("%d", &category);
    getchar(); 

    if (category < 1 || category > MAX_CATEGORIES) {
        printf("Invalid category. Please try again.\n");
        return;
    }

    displayItemsByCategory(category - 1);
}

void displayItemsByCategory(int category) {
    printf("\nItems in category:\n");
    printf("%-5s %-20s %-10s\n", "ID", "Name", "Price (Rs)");
    for (int i = 0; i < MAX_ITEMS_PER_CATEGORY; i++) {
        printf("%-5d %-20s Rs%-10.2f\n", i + 1, availableItems[category][i].name, availableItems[category][i].price);
    }

    addItemToCart();
}

void addItemToCart() {
    if (itemCount >= MAX_ITEMS) {
        printf("Cart is full. Cannot add more items.\n");
        return;
    }

    int category, itemID, quantity;
    printf("Enter the category number from which you want to add items: ");
    scanf("%d", &category);
    getchar(); 

    if (category < 1 || category > MAX_CATEGORIES) {
        printf("Invalid category. Please try again.\n");
        return;
    }

    printf("Enter the ID of the item you want to add: ");
    scanf("%d", &itemID);
    getchar(); 

    if (itemID < 1 || itemID > MAX_ITEMS_PER_CATEGORY) {
        printf("Invalid item ID. Please try again.\n");
        return;
    }

    printf("Enter quantity: ");
    scanf("%d", &quantity);
    getchar(); 

    
    for (int i = 0; i < itemCount; i++) {
        if (strcmp(cart[i].name, availableItems[category - 1][itemID - 1].name) == 0) {
            cart[i].quantity += quantity; // Increase quantity
            printf("Updated item quantity in cart.\n");
            return;
        }
    }

    
    CartItem newItem;
    strcpy(newItem.name, availableItems[category - 1][itemID - 1].name);
    newItem.price = availableItems[category - 1][itemID - 1].price;
    newItem.quantity = quantity;

    cart[itemCount++] = newItem;
    printf("Item added to cart.\n");
}

void viewCart() {
    if (itemCount == 0) {
        printf("Cart is empty.\n");
        return;
    }

    printf("\nItems in cart:\n");
    printf("%-20s %-10s %-10s %-10s\n", "Name", "Price (Rs)", "Quantity", "Total Price (Rs)");
    for (int i = 0; i < itemCount; i++) {
        float totalPrice = cart[i].price * cart[i].quantity;
        printf("%-20s Rs%-10.2f %-10d Rs%-10.2f\n", cart[i].name, cart[i].price, cart[i].quantity, totalPrice);
    }
}

void saveCartToFile(const char* username) {
    char filename[MAX_USERNAME + 10];
    sprintf(filename, "%s_cart.txt", username);

    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        perror("Error opening file");
        exit(1);
    }

    fwrite(&itemCount, sizeof(int), 1, file);
    fwrite(cart, sizeof(CartItem), itemCount, file);
    fclose(file);
}

void loadCartFromFile(const char* username) {
    char filename[MAX_USERNAME + 10];
    sprintf(filename, "%s_cart.txt", username);

    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("No existing cart file found for this user. Starting a new cart.\n");
        return;
    }

    fread(&itemCount, sizeof(int), 1, file);
    fread(cart, sizeof(CartItem), itemCount, file);
    fclose(file);
}

void clearCart() {
    itemCount = 0;
    printf("Cart cleared.\n");
}

int isPasswordStrong(const char* password) {
    int hasUpper = 0, hasLower = 0, hasDigit = 0, hasSpecial = 0;
    size_t length = strlen(password);

    if (length < 8) {
        return 0;
    }

    for (size_t i = 0; i < length; i++) {
        if (isupper(password[i])) {
            hasUpper = 1;
        } else if (islower(password[i])) {
            hasLower = 1;
        } else if (isdigit(password[i])) {
            hasDigit = 1;
        } else if (ispunct(password[i])) {
            hasSpecial = 1;
        }
    }

    return hasUpper && hasLower && hasDigit && hasSpecial;
}

