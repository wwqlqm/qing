import React from 'react'
import  {Route,Switch} from 'react-router-dom'
import PlayMovies from './playmovies'
class Movies extends React.Component{
    render() {
        return (
            <Switch>
                <Route path={this.props.match.path} component={PlayMovies}></Route>
                {/*<Route></Route>*/}
                {/*<Route></Route>*/}
            </Switch>
        )
    }
}
export  default  Movies
