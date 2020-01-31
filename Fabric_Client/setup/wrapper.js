/*
 * Copyright 2019  ChainLab
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

const config = require('./config.json')
console.log(config)

const userName = config.userName;
const connector = require(__dirname + '/connector')


/**
 * module description
 * @module Bench
 */
class Bench {

    /**
     * Always launch after instantiating
     */
    async init() {
        await connector.init(userName)
    }

    /**
     * Always launch after completion
     */
    async close() {
        await connector.disconnect()
    }

    /**
     * Private Matrix Multiplication
     * @param value
     * @param account
     * @param array of public keys for private transactions
     */
    async queryMatrixMultiplicationPublic(value) {
        let returnValue = await connector.query(['matrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };


    async queryMatrixMultiplicationPrivate(value) {
        let returnValue = await connector.query(['matrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };

    async invokeMatrixMultiplicationPublic(value) {
        let returnValue = await connector.submit(['matrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };

    async invokeMatrixMultiplicationPrivate(value) {
        let returnValue = await connector.submit(['matrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };

    async setMatrixMultiplicationPublic(value) {
        let returnValue = await connector.submit(['setMatrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };

    async setMatrixMultiplicationPrivate(value) {
        let returnValue = await connector.submit(['setMatrixMultiplication', value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue)
    };


    /**
    * Doing Nothing
    * @param account
    * @param array of public keys for private transactions
    */

    async queryDoNothingPublic() {
        let returnValue = await connector.query(['doNothing']).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async queryDoNothingPrivate() {
        let returnValue = await connector.query(['doNothing']).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async invokeDoNothingPublic() {
        let returnValue = await connector.submit(['doNothing']).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async invokeDoNothingPrivate() {
        let returnValue = await connector.submit(['doNothing']).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    /**
     * writing data
     * @param key
     * @param value
     * @param account
     * @param array of public keys for private transactions
     */

    async writeDataPublic(key, value) {
        let returnValue = await connector.submit(['writeData', key.toString(), value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async writeDataPrivate(key, value) {
        let returnValue = await connector.submit(['writeData', key.toString(), value.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    /**
    * reading data
    * @param key
    * @param account
    * @param array of public keys for private transactions
    */

    async readDataPublic(key) {
        let returnValue = await connector.query(['readData', key.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async readDataPrivate(key) {
        let returnValue = await connector.query(['readData', key.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    /**
    * writingMuchData
    * @params start, end
    * @param account
    * @param array of public keys for private transactions
    */

    async writeMuchDataPublic(len, start, delta) {
        let returnValue = await connector.submit(['writeMuchData', len.toString(), start.toString(), delta.toString()]).catch(err => { return Promise.reject(err) });
        console.log("returnValue" + returnValue);
        if (returnValue == "Cannot read property 'submitTransaction' of undefined") {
            return Promise.reject("-1")}
        return Promise.resolve(returnValue);
    }

    async writeMuchDataPrivate(len, start, delta) {
        let returnValue = await connector.submit(['writeMuchData', len.toString(), start.toString(), delta.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async writeMuchDataPublic2(len, start, delta) {
        let returnValue = await connector.submit(['writeMuchData2', len.toString(), start.toString(), delta.toString()]).catch(err => { return Promise.reject(err) });
        console.log("returnValue" + returnValue);
        if (returnValue == "Cannot read property 'submitTransaction' of undefined") {
            return Promise.reject("-1")}
        return Promise.resolve(returnValue);
    }

    async writeMuchDataPrivate2(len, start, delta) {
        let returnValue = await connector.submit(['writeMuchData2', len.toString(), start.toString(), delta.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    /**
    * readingMuchData
    * @params start, end
    * @param account
    * @param array of public keys for private transactions
    */

    async readMuchDataPublic(len, start) {
        let returnValue = await connector.query(['readMuchData', len.toString(), start.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async readMuchDataPrivate(len, start) {
        let returnValue = await connector.query(['readMuchData', len.toString(), start.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async readMuchDataPublic2(len, start) {
        let returnValue = await connector.query(['readMuchData2', len.toString(), start.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

    async readMuchDataPrivate2(len, start) {
        let returnValue = await connector.query(['readMuchData2', len.toString(), start.toString()]).catch(err => { return Promise.reject(err) });
        return Promise.resolve(returnValue);
    }

}

module.exports = Bench;
