import './App.css';

import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import Leaderboard from "./views/leaderboard/leaderboard";
import Profile from "./views/profile/profile"


function App() {
  return (
    <Router>
      <Switch>
        <Route
          path="/user/profile/:user_id"
          render={(props) => (
            <div>
              <Profile {...props} />
            </div>
          )}
        />
      </Switch>
    </Router>
  );
}

export default App;
