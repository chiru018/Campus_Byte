import React, { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext(null);

const CART_STORAGE_KEY = 'campusbyte_cart_v1';
const STANDARD_DELIVERY_FEE = 2.0;

export const CartProvider = ({ children }) => {
  const [restaurant, setRestaurant] = useState(null);
  const [items, setItems] = useState([]);
  const [conflictModal, setConflictModal] = useState({
    isOpen: false,
    newRestaurant: null,
    pendingItem: null,
  });

  // Load persisted cart on startup
  useEffect(() => {
    try {
      const stored = localStorage.getItem(CART_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && Array.isArray(parsed.items) && parsed.restaurant) {
          setRestaurant(parsed.restaurant);
          setItems(parsed.items);
        }
      }
    } catch (err) {
      console.warn('Failed to parse cached cart data', err);
      localStorage.removeItem(CART_STORAGE_KEY);
    }
  }, []);

  // Sync cart to localStorage whenever it changes
  useEffect(() => {
    try {
      if (items.length > 0 && restaurant) {
        localStorage.setItem(
          CART_STORAGE_KEY,
          JSON.stringify({ restaurant, items })
        );
      } else {
        localStorage.removeItem(CART_STORAGE_KEY);
      }
    } catch (err) {
      console.warn('Failed to sync cart data to storage', err);
    }
  }, [restaurant, items]);

  /**
   * Add an item to the shopping cart.
   * If cart already has items from another restaurant, opens conflict modal.
   */
  const addToCart = (item, restInfo) => {
    // Check if adding from a different restaurant
    if (restaurant && restaurant.id !== restInfo.id && items.length > 0) {
      setConflictModal({
        isOpen: true,
        newRestaurant: restInfo,
        pendingItem: item,
      });
      return false;
    }

    // Set restaurant if first item
    if (!restaurant || items.length === 0) {
      setRestaurant({
        id: restInfo.id,
        name: restInfo.name,
        address: restInfo.address,
      });
    }

    setItems((prevItems) => {
      const existing = prevItems.find((i) => i.id === item.id);
      if (existing) {
        return prevItems.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      } else {
        return [
          ...prevItems,
          {
            id: item.id,
            name: item.name,
            price: parseFloat(item.price),
            image_url: item.image_url,
            category: item.category,
            quantity: 1,
            restaurant_id: restInfo.id,
          },
        ];
      }
    });

    return true;
  };

  /**
   * Confirm switching restaurants: clears existing items and adds new item.
   */
  const confirmRestaurantSwitch = () => {
    if (!conflictModal.newRestaurant || !conflictModal.pendingItem) return;

    setRestaurant({
      id: conflictModal.newRestaurant.id,
      name: conflictModal.newRestaurant.name,
      address: conflictModal.newRestaurant.address,
    });

    setItems([
      {
        id: conflictModal.pendingItem.id,
        name: conflictModal.pendingItem.name,
        price: parseFloat(conflictModal.pendingItem.price),
        image_url: conflictModal.pendingItem.image_url,
        category: conflictModal.pendingItem.category,
        quantity: 1,
        restaurant_id: conflictModal.newRestaurant.id,
      },
    ]);

    setConflictModal({ isOpen: false, newRestaurant: null, pendingItem: null });
  };

  const cancelRestaurantSwitch = () => {
    setConflictModal({ isOpen: false, newRestaurant: null, pendingItem: null });
  };

  /**
   * Update item quantity directly.
   */
  const updateQuantity = (itemId, newQty) => {
    if (newQty <= 0) {
      removeFromCart(itemId);
      return;
    }

    setItems((prevItems) =>
      prevItems.map((i) => (i.id === itemId ? { ...i, quantity: newQty } : i))
    );
  };

  /**
   * Remove a single item from the cart.
   */
  const removeFromCart = (itemId) => {
    setItems((prevItems) => {
      const updated = prevItems.filter((i) => i.id !== itemId);
      if (updated.length === 0) {
        setRestaurant(null);
      }
      return updated;
    });
  };

  /**
   * Clear the entire cart.
   */
  const clearCart = () => {
    setItems([]);
    setRestaurant(null);
    localStorage.removeItem(CART_STORAGE_KEY);
  };

  // Derived Totals
  const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotal = items.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  const deliveryFee = totalItems > 0 ? STANDARD_DELIVERY_FEE : 0.0;
  const totalAmount = totalItems > 0 ? subtotal + deliveryFee : 0.0;

  const getItemQuantity = (itemId) => {
    const found = items.find((i) => i.id === itemId);
    return found ? found.quantity : 0;
  };

  return (
    <CartContext.Provider
      value={{
        restaurant,
        items,
        totalItems,
        subtotal,
        deliveryFee,
        totalAmount,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        getItemQuantity,
        conflictModal,
        confirmRestaurantSwitch,
        cancelRestaurantSwitch,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export default CartContext;

