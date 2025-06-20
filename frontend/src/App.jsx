import { Provider } from "react-redux";
import store, { persistor } from "./redux/store";
import { PersistGate } from "redux-persist/integration/react";
import { BrowserRouter, useRoutes } from "react-router-dom";
import MainRoutes from "./routes/MainRoutes";

function AppRoutes() {
  const routes = useRoutes(MainRoutes);
  return routes;
}

function App() {
  return (
    <Provider store={store}>
      <PersistGate persistor={persistor}>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </PersistGate>
    </Provider>
  );
}

export default App;
