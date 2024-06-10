=======
/**
 * This file is a modified version of https://github.com/aghadiry/serverless-cloudfront-invalidate,
 * which is licensed under the MIT license.
 *
 * MIT License
 *
 * Copyright (c) 2017 aghadiry
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

'use strict';

const randomstring = require('randomstring');
const chalk = require('chalk');
const fs = require('fs');
const https = require('https');
const proxy = require('proxy-agent');

class CloudfrontInvalidate {

  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options || {};
    this.proxyURL =
      process.env.proxy ||
      process.env.HTTP_PROXY ||
      process.env.http_proxy ||
      process.env.HTTPS_PROXY ||
      process.env.https_proxy;
    this.provider = 'aws';
    this.aws = this.serverless.getProvider('aws');

    if (this.proxyURL) {
      this.setProxy(this.proxyURL);
    }

    if (this.options.cacert) {
      this.handleCaCert(this.options.cacert);
    }

    this.commands = {
      cloudfrontInvalidate: {
        usage: "Invalidate Cloudfront Cache",
        lifecycleEvents: [
          'invalidate'
        ]
      }
    };

    this.hooks = {
      'cloudfrontInvalidate:invalidate': this.invalidate.bind(this),
      'after:deploy:deploy': this.afterDeploy.bind(this),
    };
  }

  setProxy(proxyURL) {
    this.aws.sdk.config.update({
      httpOptions: { agent: proxy(proxyURL) },
    });
  }

  handleCaCert(caCert) {
    const cli = this.serverless.cli;

    if (!fs.existsSync(caCert)) {
      throw new Error("Supplied cacert option to a file that does not exist: " + caCert);
    }

    this.aws.sdk.config.update({
      httpOptions: { agent: new https.Agent({ ca: fs.readFileSync(caCert) }) }
    });

    cli.consoleLog(`CloudfrontInvalidate: ${chalk.yellow('ca cert handling enabled')}`);
  }

  createInvalidation(distributionId, reference, cloudfrontInvalidate) {
    const cli = this.serverless.cli;
    const cloudfrontInvalidateItems = cloudfrontInvalidate.items;

    const params = {
      DistributionId: distributionId, /* required */
      InvalidationBatch: { /* required */
        CallerReference: reference, /* required */
        Paths: { /* required */
          Quantity: cloudfrontInvalidateItems.length, /* required */
          Items: cloudfrontInvalidateItems
        }
      }
    };
    return this.aws.request('CloudFront', 'createInvalidation', params).then(
      () => {
        cli.consoleLog(`CloudfrontInvalidate: ${chalk.yellow('Invalidation started')}`);
      },
      err => {
        cli.consoleLog(JSON.stringify(err));
        cli.consoleLog(`CloudfrontInvalidate: ${chalk.yellow('Invalidation failed')}`);
        throw err;
      }
    );
  }

  invalidateElements(elements) {
    const cli = this.serverless.cli;

    if (this.options.noDeploy) {
      cli.consoleLog('skipping invalidation due to noDeploy option');
      return;
    }

    const invalidationPromises = elements.map(element => {
      let cloudfrontInvalidate = element;
      let reference = randomstring.generate(16);
      let distributionId = cloudfrontInvalidate.distributionId;
      let stage = cloudfrontInvalidate.stage;

      if (stage !== undefined && stage !== `${this.serverless.service.provider.stage}`) {
        return;
      }

      if (distributionId) {
        cli.consoleLog(`DistributionId: ${chalk.yellow(distributionId)}`);

        return this.createInvalidation(distributionId, reference, cloudfrontInvalidate);
      }

      if (!cloudfrontInvalidate.distributionIdKey) {
        cli.consoleLog('distributionId or distributionIdKey is required');
        return;
      }

      cli.consoleLog(`DistributionIdKey: ${chalk.yellow(cloudfrontInvalidate.distributionIdKey)}`);

      // get the id from the output of stack.
      const stackName = this.serverless.getProvider('aws').naming.getStackName()

      return this.aws.request('CloudFormation', 'describeStacks', { StackName: stackName })
        .then(result => {
          if (result) {
            const outputs = result.Stacks[0].Outputs;
            outputs.forEach(output => {
              if (output.OutputKey === cloudfrontInvalidate.distributionIdKey) {
                distributionId = output.OutputValue;
              }
            });
          }
        })
        .then(() => this.createInvalidation(distributionId, reference, cloudfrontInvalidate))
        .catch(() => {
          cli.consoleLog('Failed to get DistributionId from stack output. Please check your serverless template.');
        });
    });

    return Promise.all(invalidationPromises);
  }

  afterDeploy() {
    const elementsToInvalidate = this.serverless.service.custom.cloudfrontInvalidate
      .filter((element) => {
        if (element.autoInvalidate !== false) {
          return true;
        }

        this.serverless.cli.consoleLog(`Will skip invalidation for the distributionId "${element.distributionId || element.distributionIdKey}" as autoInvalidate is set to false.`);
        return false;
      });

    return this.invalidateElements(elementsToInvalidate);
  }

  invalidate() {
    return this.invalidateElements(this.serverless.service.custom.cloudfrontInvalidate);
  }
}

module.exports = CloudfrontInvalidate;
