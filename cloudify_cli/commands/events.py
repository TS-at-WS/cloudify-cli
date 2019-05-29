########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############

from cloudify_rest_client.exceptions import CloudifyClientError

import click

from .. import utils
from ..cli import cfy
from ..logger import get_events_logger
from ..exceptions import CloudifyCliError, SuppressedCloudifyCliError
from ..execution_events_fetcher import ExecutionEventsFetcher, \
    wait_for_execution


@cfy.group(name='events')
@cfy.options.common_options
@cfy.assert_manager_active()
def events():
    """Show events from workflow executions
    """
    pass


@events.command(name='list',
                short_help='List deployments events [manager only]')
@cfy.options.execution_id_argument(required=False)
@cfy.options.execution_id(required=False, dest='execution_id_opt')
@cfy.options.include_logs
@cfy.options.json_output
@cfy.options.tail
@cfy.options.common_options
@cfy.options.tenant_name(required=False, resource_name_for_help='execution')
@cfy.options.pagination_offset
@cfy.options.pagination_size
@cfy.pass_client()
@cfy.pass_logger
def list(execution_id,
         execution_id_opt,
         include_logs,
         json_output,
         tail,
         tenant_name,
         pagination_offset,
         pagination_size,
         client,
         logger):
    """Show events of the given execution.

    `EXECUTION_ID` is the execution to get events for.
    Execution ID can also be the workflow name to use the most recent
    execution of that workflow.
    """
    if execution_id and execution_id_opt:
        raise click.UsageError(
            "Execution ID provided both as a positional "
            "argument ('{}') and as an option ('{}'). "
            "Please only specify it once (preferably as "
            "a positional argument).".format(
                execution_id,
                execution_id_opt))

    if not execution_id:
        execution_id = execution_id_opt
        if not execution_id:
            raise click.UsageError('Execution ID not provided')
        logger.warning("Providing the execution ID as an option (using '-e') "
                       "is now deprecated. Please provide the execution ID as "
                       "a positional argument.")

    """Display events for an execution
    """
    utils.explicit_tenant_name_message(tenant_name, logger)
    logger.info('Listing events for execution id {0} '
                '[include_logs={1}]'.format(execution_id, include_logs))
    try:
        execution_events = ExecutionEventsFetcher(
            client,
            execution_id,
            include_logs=include_logs
        )

        events_logger = get_events_logger(json_output)

        if tail:
            execution = wait_for_execution(client,
                                           client.executions.get(execution_id),
                                           events_handler=events_logger,
                                           include_logs=include_logs,
                                           timeout=None)  # don't timeout ever
            if execution.error:
                logger.info('Execution of workflow {0} for deployment '
                            '{1} failed. [error={2}]'.format(
                                execution.workflow_id,
                                execution.deployment_id,
                                execution.error))
                raise SuppressedCloudifyCliError()
            else:
                logger.info('Finished executing workflow {0} on deployment '
                            '{1}'.format(
                                execution.workflow_id,
                                execution.deployment_id))
        else:
            # don't tail, get only the events created until now and return
            current_events, total_events = execution_events. \
                fetch_and_process_events_batch(events_handler=events_logger,
                                               offset=pagination_offset,
                                               size=pagination_size)
            logger.info('\nShowing {0} of {1} events'.format(current_events,
                                                             total_events))
            if not json_output:
                logger.info('Debug messages are only shown when you use very '
                            'verbose mode (-vv)')
    except CloudifyClientError as e:
        if e.status_code != 404:
            raise
        raise CloudifyCliError('Execution {0} not found'.format(execution_id))


@events.command(name='delete',
                short_help='Delete deployment events [manager only]')
@cfy.argument('deployment-id')
@cfy.options.include_logs
@cfy.options.common_options
@cfy.options.tenant_name(required=False, resource_name_for_help='deployment')
@cfy.pass_client()
@cfy.pass_logger
def delete(deployment_id, include_logs, logger, client, tenant_name):
    """Delete events attached to a deployment

    `EXECUTION_ID` is the execution events to delete.
    """
    utils.explicit_tenant_name_message(tenant_name, logger)
    logger.info(
        'Deleting events for deployment id {0} [include_logs={1}]'.format(
            deployment_id, include_logs))

    # Make sure the deployment exists - raise 404 otherwise
    client.deployments.get(deployment_id)
    deleted_events_count = client.events.delete(
        deployment_id, include_logs=include_logs
    )
    deleted_events_count = deleted_events_count.items[0]
    if deleted_events_count:
        logger.info('\nDeleted {0} events'.format(deleted_events_count))
    else:
        logger.info('\nNo events to delete')
