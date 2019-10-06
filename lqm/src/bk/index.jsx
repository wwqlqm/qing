import React from 'react'
import  {Route,Switch} from 'react-router-dom'
import SHOWBK from './showbk/showbks'
import WRITEBK from './writebk/writebk'
class BK extends React.Component{
    render() {
        return (
            <Switch>
                <Route path={this.props.match.path + '/writebk'} component={WRITEBK}></Route>
                <Route path={this.props.match.path} component={SHOWBK}></Route>
                {/*<Route></Route>*/}
                {/*<Route></Route>*/}
            </Switch>
        )
    }
}
export  default  BK
