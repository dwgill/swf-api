import * as _ from 'lodash';
import { ValueTransformer } from 'typeorm/decorator/options/ValueTransformer';

export const deserialize = (str: string) => _(str || '').split(';;').filter(_.identity).value();

export const serialize = (strs: string[]) => _(strs).filter(_.identity).join(';;') || null;

export const transformer: ValueTransformer = {
    from: deserialize,
    to: serialize,
};
