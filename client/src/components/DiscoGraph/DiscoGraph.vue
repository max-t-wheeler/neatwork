<template>
  <div id='container'>
    <toolbar id='toolbar'/>
    <b-container fluid id='discograph-container'>
      <navpane
        id='discograph-options'
        v-bind='{onReload, onSearch, onSubmit, parameters, queryData, toFullScreen}'
        @onSubmit='onSubmit($event)'
      />
      <b-row>
        <b-col id='discograph-context'>
          <chart
            v-if='display.graph'
            id='discograph-display'
            v-bind='{graph, graphLastUpdated}'
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
        loading: false,
      },
      failureMessage: '',
      graph: null,
      graphLastUpdated: null,
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
    onGraphUpdate() {
      this.graphLastUpdated = Date.now();
    },
    onReload(event) {
      event.preventDefault();

      if (this.graph) {
        console.log(this.graph);
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

      getSearchResults(payload)
      .then((queryData) => {
          this.queryData = queryData;
          console.log('Search results retrieved');
      })
      .catch((error) => {
          this.display.loading = false;
          this.failureMessage = 'Failed to retrieve search results';
          this.display.failureMessage = true;
          console.log(error);
      });
    },
    onSubmit() {
      if (this.display.graph) this.display.graph = false;

      this.graph = new Graph(
        this.parameters.connection,
        this.parameters.numSteps,
        this.parameters.sourceId,
        this.parameters.sourceType,
        this.parameters.targetType,
        this.onGraphUpdate.bind(this),
      );

      this.graph.generate();
      this.display.graph = true;
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
