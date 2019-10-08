<template>
  <div id='container'>
    <toolbar id='toolbar'/>
    <b-container fluid id='discograph-container'>
      <navpane
        v-if='display.inputs'
        id='discograph-options'
        v-bind='{onReload, onSearch, onSubmit, parameters, queryData, toFullScreen}'
        @onSubmit='onSubmit($event)'
      />
      <b-row v-if='display.inputs'>
        <b-col id='discograph-context'>
          <chart
            v-if='display.graph'
            id='discograph-display'
            v-bind='{graphData, nodeData, parameters}'
          />
          <div v-if='display.loading' id="loading-icon">
            <socket/>
            <p>Generating graph data...</p>
          </div>
          <div v-if='display.failureMessage' id='failure-message'>
            <p>{{ failureMessage }}</p>
          </div>
        </b-col>
      </b-row>
      <footer id='footer'>
        <p>Discograph</p>
      </footer>
    </b-container>
  </div>
</template>

<script>
import axios from 'axios';
import { Socket } from 'vue-loading-spinner';

import Graph from './graph';
import { getGraphData, getSearchResults } from './requests';

import Chart from './Chart.vue';
import Navpane from './Navpane.vue';
import Toolbar from '../Toolbar.vue';

export default {
  name: 'DiscoGraph',
  components: {
    chart: Chart,
    navpane: Navpane,
    toolbar: Toolbar,
    socket: Socket,
  },
  data() {
    return {
      display: {
        failureMessage: false,
        graph: false,
        inputs: true,
        loading: false,
      },
      failureMessage: '',
      graphData: null,
      nodeData: null,
      queryData: null,
      parameters: {
        connection: 'association',
        name: 'Grateful Dead',
        numSteps: 1,
        sourceId: null,
        sourceType: 'artist',
        targetType: 'artist',
      },
    };
  },
  methods: {
    onReload(event) {
      event.preventDefault();

      if (this.graphData) {
        console.log(this.graphData);
      }

      if (this.display.graph) {
        console.log('In development');
      }
    },
    onSearch(event) {
      event.preventDefault();

      if (this.display.failureMessage) this.display.failureMessage = false;

      const payload = {
        count: 10,
        source_type: this.parameters.sourceType,
        text: this.parameters.name,
      };

      getSearchResults(payload, this);
    },
    onSubmit() {
      if (this.display.graph) this.display.graph = false;
      if (this.display.failureMessage) this.display.failureMessage = false;
      this.display.loading = true;

      const payload = {
        connection: this.parameters.connection,
        name: this.parameters.name,
        num_steps: this.parameters.numSteps,
        source_id: this.parameters.sourceId,
        source_type: this.parameters.sourceType,
        target_type: this.parameters.targetType,
      };

      getGraphData(payload, this);
    },
    toFullScreen() {
      const display = document.getElementById('discograph-display');

      if (display.requestFullscreen) {
        display.requestFullscreen();
      } else if (display.webkitRequestFullscreen) {
        display.webkitRequestFullscreen();
      } else if (display.mozRequestFullScreen) {
        display.mozRequestFullScreen();
      } else if (display.msRequestFullscreen) {
        display.msRequestFullscreen();
      }
    },
  },
};
</script>

<style>

#discograph-auth-text {
  width: 85%;
}

#container {
  overflow: hidden;
}

#discograph-container {
  overflow: hidden;
}

#discograph-context {
  height: 80vh;
  position: relative;
  text-align: center;
  padding: 0px;
}

#discograph-display:fullscreen {
  background-color: white;
}

#loading-icon {
  position: relative;
  display: inline-flex;
  top: 250px;
}

#failure-message {
  position: relative;
  display: inline-flex;
  top: 250px;
}

#footer {
  text-align: center;
}
</style>
