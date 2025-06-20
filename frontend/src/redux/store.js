import { configureStore } from '@reduxjs/toolkit';
import storage from 'redux-persist/lib/storage';
import autoMergeLevel1 from 'redux-persist/lib/stateReconciler/autoMergeLevel1';
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
import mainReducer from './mainReducer';

const persistConfig = {
  key: 'root',
  storage,
  stateReconciler: autoMergeLevel1,
  whitelist: ['menu', 'auth'],
  blacklist: [],
  debug: true
};

const middleware = (getDefaultMiddleware) =>
  getDefaultMiddleware({
    immutableCheck: false,
    serializableCheck: {
      ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER]
    }
  });

const store = configureStore({
  reducer: persistReducer(persistConfig, mainReducer()),
  middleware,
  devTools: true
});

export const persistor = persistStore(store);
export default store;
