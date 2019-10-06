import React from 'react'
import  {Route,Switch} from 'react-router-dom'
import MusicContent from './musiccontent/musicscontent'
class Music extends React.Component{
    render() {
        return (
            <Switch>
                <Route path={this.props.match.path} component={MusicContent}></Route>
                {/*<Route></Route>*/}
                {/*<Route></Route>*/}
            </Switch>
        )
    }
}
export  default  Music
