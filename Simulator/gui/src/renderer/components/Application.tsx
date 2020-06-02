import { hot } from 'react-hot-loader/root';
import * as React from 'react';
import AppLayout from './AppLayout/AppLayout';

// const { useEffect } = React;

/// here we get all the info required and pass it as props to the children


const Application = () => {
    return (
        <div>
            <AppLayout />
        </div>

    )
};

export default hot(Application);
