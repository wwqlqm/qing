import {createStore} from "redux";

var simpleReducer = function(state = {}, action) {
    return {
        user: {
            name: 'redux'
        }
    }
}

var store = createStore(simpleReducer)

console.log(store.getState())
