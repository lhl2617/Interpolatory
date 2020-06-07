import React from 'react'
import { InterpolationMode, getInterpolationModeSchema, InterpolationModeSchema, snakeCaseToFirstWordCapitalised } from '../../util'
import { message, Form, Select, Popover, InputNumber } from 'antd'

import {
    InfoCircleOutlined
} from '@ant-design/icons';
const { Option } = Select;
const { useEffect, useState, useRef } = React

type Props = {
    setIMode: (iMode: InterpolationMode) => Promise<void>;
    iMode: InterpolationMode | undefined; /// current state
    disabled: boolean;
    disabledIModeKeys: string[];
}

type State = {
    iModeSchema: InterpolationModeSchema | undefined
}

const initialState: State = {
    iModeSchema: undefined
}

const IMode = (props: Props) => {
    const mounted = useRef(true)
    const [state, _updateState] = useState(initialState)

    const updateState = (nextState: State) => {
        if (mounted.current) {
            _updateState(nextState)

        }
    }

    useEffect(() => {

        getIModeSchema()
        return () => {
            mounted.current = false
        }
    }, [])

    const getIModeSchema = async () => {
        const { disabledIModeKeys } = props
        try {
            const schemaAll = (await getInterpolationModeSchema())
            const enabledIModeKeys = Object.keys(schemaAll).filter((k) => !disabledIModeKeys.includes(k))
            let schema: Record<string, InterpolationMode> = {}
            enabledIModeKeys.forEach((k) => schema[k] = schemaAll[k])
            updateState({ iModeSchema: schema })

            const iMode = Object.values(schema)[0]
            props.setIMode(iMode)
        }
        catch (err) {
            message.error(err.message);
        }
    }

    const handleChangeIMode = (key: string) => {

        const { setIMode } = props;
        const { iModeSchema } = state;
        if (!iModeSchema) {
            message.error('Something went wrong')
            return // this should never happen
        }
        else if (!(key in iModeSchema)) {
            message.error('Invalid interpolation mode')
            return // actually should never happen as well
        }

        setIMode(iModeSchema[key])
    }

    const handleChangeIModeOption = (optKey: string, optValue: string | number) => {
        const { setIMode, iMode } = props
        if (iMode && iMode.options) {
            let newIMode = iMode;
            if (newIMode.options) {
                newIMode.options[optKey].value = optValue
                setIMode(newIMode)
            }
            else {
                message.error('Something went wrong')
                return // this should never happen
            }
        }
        else {
            message.error('Something went wrong')
            return // this should never happen
        }
    }

    const { iMode, disabled, disabledIModeKeys } = props;
    const { iModeSchema } = state;
    return (
        <div>
            <Form.Item
                help={iMode ? iMode.description : ``}
                label={<h3>Interpolation Mode</h3>}>
                <Select disabled={disabled || !iMode} value={iMode?.name} onChange={handleChangeIMode}>
                    {
                        iModeSchema && (
                            Object.values(iModeSchema)
                                .map((m) => {
                                    return (<Option key={m.name} value={m.name} title={m.description}>{m.name}</Option>)
                                }))
                    }
                </Select>
            </Form.Item>
            {
                iMode && iMode.options &&
                Object.entries(iMode.options).map(([key, opt]) => {
                    if (opt.type === `enum`) {
                        return (
                            <Form.Item
                                key={key}
                                label={
                                    <Popover content={<div>{opt.description}</div>} trigger="hover"><h3>{snakeCaseToFirstWordCapitalised(key)} <InfoCircleOutlined /></h3></Popover>}
                            >
                                <Select disabled={disabled || !iMode} value={opt.value} onChange={(optionValue) => handleChangeIModeOption(key, optionValue)}>
                                    {
                                        Object.values(opt.enum).map((m, idx) => {
                                            return (<Option key={m} value={m} title={opt.enumDescriptions[idx]}>{m}</Option>)
                                        })
                                    }
                                </Select>
                            </Form.Item>
                        )
                    }
                    else if (opt.type === `number`) {
                        return (
                            <Form.Item
                                key={key}
                                label={
                                    <Popover content={<div>{opt.description}</div>} trigger="hover"><h3>{snakeCaseToFirstWordCapitalised(key)} <InfoCircleOutlined /></h3></Popover>}
                            >
                                <InputNumber disabled={disabled || !iMode} min={0} step={1} onChange={(optionValue) => optionValue && handleChangeIModeOption(key, optionValue)} value={opt.value} />

                            </Form.Item>
                        )
                    }
                    /// should not have other cases....
                })
            }
        </div>
    )
}

export default IMode