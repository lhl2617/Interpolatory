/* eslint-disable */
import * as React from 'react';
import { Layout, Menu, Button } from 'antd';
import { remote } from 'electron';
import Benchmark from '../Pages/Benchmark/Benchmark';
import Convert from '../Pages/Convert/Convert';
import Test from '../Pages/Test/Test';
import Info from '../Pages/Info/Info';

const { SubMenu } = Menu;
const { Header, Content, Sider } = Layout;

const logo = require('../../../../assets/img/headerlogo.png').default;
const convertIcon = require('../../../../assets/img/convert.png').default;
const benchmarkIcon = require('../../../../assets/img/benchmark.png').default;
const testIcon = require('../../../../assets/img/test.png').default;
const infoIcon = require('../../../../assets/img/info.png').default;


const minIcon = require('../../../../assets/img/window/min.png').default;
const maxIcon = require('../../../../assets/img/window/max.png').default;
const closeIcon = require('../../../../assets/img/window/close.png').default;


type CurrentPage = 'convert' | 'benchmark' | 'test' | 'info';

type IState = {
    currentPage: CurrentPage;
    height: number;
};

export class AppLayout extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            currentPage: 'convert',
            height: 600,
        };
    }

    componentDidMount = () => {
        this.updateWindowDimensions();
        window.addEventListener('resize', this.updateWindowDimensions);

        // window.addEventListener('keydown', (e) => {
        //     if (e.which === 123) {
        //         require('remote').getCurrentWindow().toggleDevTools();
        //     } 
        // })
    }

    componentWillUnmount = () => {
        window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions = () => {
        this.setState({ height: window.innerHeight });
    }

    closeApp = () => {
        const w = remote.getCurrentWindow();
        w.close();
    }

    minApp = () => {
        const w = remote.getCurrentWindow();
        w.minimize();
    }

    maxApp = () => {
        const w = remote.getCurrentWindow();
        if (!w.isMaximized()) {
            w.maximize();
        } else {
            w.unmaximize();
        }
    }

    getContent = (currentPage: CurrentPage) => {
        if (currentPage === "benchmark") return <Benchmark />;
        if (currentPage === "convert") return <Convert />;
        if (currentPage === "test") return <Test />;
        if (currentPage === "info") return <Info />;
        console.error('Invalid currentPage');
    }

    gotoPage = (page: CurrentPage) => {
        this.setState({
            currentPage: page
        })
    }

    render() {
        const { currentPage, height } = this.state;
        return (
            <Layout>
                <Header className="header">
                    <img
                        id='header-logo'
                        src={logo}
                        alt='Interpolatory Simulator'
                    />
                    <div style={{ float: 'right', color: 'white' }}>
                        <img className="window-btn" onClick={this.minApp} src={minIcon} alt="Min" />
                        <img className="window-btn" onClick={this.maxApp} src={maxIcon} alt="Max" />
                        <img className="window-btn" onClick={this.closeApp} src={closeIcon} alt="Close" />
                    </div>

                </Header>
                <Layout className="app-content">
                    <Sider width={200} className="site-layout-background">
                        <Menu
                            mode="inline"
                            defaultSelectedKeys={['1']}
                            theme="dark"
                            style={{ height: '100%', borderRight: 0 }}>
                            <Menu.Item 
                                key="1" 
                                icon={<img className="menu-icon" src={convertIcon} alt='Convert' />} 
                                onClick={() => this.gotoPage('convert')}>
                                    Convert
                            </Menu.Item>
                            <Menu.Item 
                                key="2" 
                                icon={<img className="menu-icon" src={benchmarkIcon} alt='Benchmark' />} 
                                onClick={() => this.gotoPage('benchmark')}>
                                    Benchmark
                            </Menu.Item>
                            <Menu.Item 
                                key="3" 
                                icon={<img className="menu-icon" src={testIcon} alt='Test' />} 
                                onClick={() => this.gotoPage('test')}>
                                    Test
                            </Menu.Item>
                            <Menu.Item 
                                key="4" 
                                icon={<img className="menu-icon" src={infoIcon} alt='Info' />} 
                                onClick={() => this.gotoPage('info')}>
                                    Info
                            </Menu.Item>
                        </Menu>
                    </Sider>
                    <Layout style={{ padding: '0 24px 24px', minHeight: height - 50 }}>
                        <Content
                            className="site-layout-background"
                            style={{
                                padding: 24,
                                margin: 0,
                            }}>
                            {this.getContent(currentPage)}
                        </Content>
                    </Layout>
                </Layout>
            </Layout>
        );
    }
}

export default AppLayout;
