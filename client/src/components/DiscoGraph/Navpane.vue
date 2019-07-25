<template>
  <div>
    <b-row>
      <b-col>
      <b-form-select
        v-model='parameters.connection'
        class='discograph-navpane'
        :options='connection.dropdown'
      />
      </b-col>
      <b-col>
        <b-form-select
          v-model='parameters.sourceType'
          class='discograph-navpane'
          :options='sourceOptions'
        />
      </b-col>
      <b-col>
      <b-form-select
        v-model='parameters.targetType'
        class='discograph-navpane'
        :options='targetOptions'
      />
      </b-col>
    </b-row>
    <b-row>
      <b-col
      v-if='this.parameters.connection == "association"
      && this.parameters.sourceType == this.parameters.targetType'
      >
        <input
          id='discograph-number-input'
          class='discograph-navpane'
          v-model='parameters.numSteps'
          type='number'
          :max='depth.max'
          :min='depth.min'
          v-on:blur='resetDepth()'
        >
      </b-col>
      <b-col>
        <input
          v-model='parameters.name'
          class='discograph-navpane'
          placeholder='Enter an artist...'
        >
      </b-col>
      <b-col>
        <b-button @click='onSubmit'>
          <font-awesome-icon icon='play-circle'></font-awesome-icon>
        </b-button>
        <b-button @click='onReload'>
          <font-awesome-icon icon='sync'></font-awesome-icon>
        </b-button>
        <b-button @click='toFullScreen'>
          <font-awesome-icon icon='arrows-alt'></font-awesome-icon>
        </b-button>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowsAlt, faPlayCircle, faSync } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faArrowsAlt);
library.add(faPlayCircle);
library.add(faSync);

export default {
  name: 'Navpane',
  props: ['parameters', 'onSubmit', 'onReload', 'toFullScreen'],
  components: {
    'font-awesome-icon': FontAwesomeIcon,
  },
  data() {
    return {
      connection: {
        dropdown: [
          {
            text: 'Association',
            value: 'association',
          },
          {
            text: 'Collaboration',
            value: 'collaboration',
          },
          {
            text: 'Discograhy',
            value: 'discography',
          },
        ],
      },
      depth: {
        display: true,
        max: 3,
        min: 1,
      },
      nodeType: {
        dropdown: [
          {
            text: 'Artist',
            value: 'artist',
          },
          {
            text: 'Label',
            value: 'label',
          },
          {
            text: 'Master',
            value: 'master',
          },
          {
            text: 'Release',
            value: 'release',
          },
        ],
      },
    };
  },
  computed: {
    sourceOptions() {
      let options;
      if (this.parameters.connection === 'collaboration') {
        options = this.nodeType.dropdown.slice(0, 1);
      } else {
        options = this.nodeType.dropdown.slice(0, 2);
      }
      // eslint-disable-next-line
      this.parameters.sourceType = options[0].value;
      return options;
    },
    targetOptions() {
      let options;
      if (this.parameters.connection === 'association') {
        options = this.nodeType.dropdown.slice(0, 2);
      } else if (this.parameters.connection === 'collaboration') {
        options = this.nodeType.dropdown.slice(0, 1);
      } else {
        options = this.nodeType.dropdown.slice(2, 4);
      }
      // eslint-disable-next-line
      this.parameters.targetType = options[0].value;
      return options;
    },
  },
  methods: {
    resetDepth() {
      if (this.parameters.numSteps > this.depth.max) {
        this.parameters.numSteps = this.depth.max;
      } else if (this.parameters.numSteps < this.depth.min) {
        this.parameters.numSteps = this.depth.min;
      }
    },
  },
};
</script>

<style>

#discograph-navpane {
  height: 90vh;
  position: relative;
  width: 100%;
  padding: 0px;
}

.discograph-navpane {
  width: 100%;
}

</style>
