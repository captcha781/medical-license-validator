import { combineReducers } from '@reduxjs/toolkit';
import auth from './slices/auth.slice';

const mainReducer = (asyncReducers) => (state, action) => {
  const combinedReducers = combineReducers({
    auth,
    ...asyncReducers
  });

  return combinedReducers(state, action);
};

export default mainReducer;
